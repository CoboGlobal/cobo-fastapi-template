#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/utils.sh"

strip_quotes() {
    echo "$1" | sed "s/^['\"]//;s/['\"]$//"
}

# Function: Validate key and secret
validate_key_and_secret() {
    local key=$(strip_quotes "$1")
    local secret=$(strip_quotes "$2")

    echo "Validating key and secret..."
    if ! cobo keys validate --secret "$secret" --pubkey "$key"; then
        print_error "Error: Validation failed for the provided key and secret."
        exit 1
    fi
    print_success "Validation successful for key and secret."
}

# Function: Check if .env file in the current directory has the required key and secret
check_env_file() {
    if [[ -f ".env" ]]; then
        # %if app_type == portal
        key=$(grep -E "^COBO_APP_KEY=" .env | cut -d'=' -f2)
        secret=$(grep -E "^COBO_APP_SECRET=" .env | cut -d'=' -f2)
        # %else
        key=$(grep -E "^COBO_API_KEY=" .env | cut -d'=' -f2)
        secret=$(grep -E "^COBO_API_SECRET=" .env | cut -d'=' -f2)
        # %endif

        if [[ -n "$key" && -n "$secret" ]]; then
            print_success "Key and secret already exist in .env file."
            validate_key_and_secret "$key" "$secret"
            return 0
        fi
    fi
    return 1
}

# %if app_type == portal
get_key_and_secret() {
    key=$(cobo app manifest -k app_key 2>/dev/null)
    if [[ "$key" == *"-"* || -z "$key" ]]; then
        print_error "Failed to retrieve APP_KEY from manifest."
        return 1
    fi

    # Try to get secret from current .env or parent .env
    if [[ -f ".env" ]]; then
        secret=$(grep -E "^COBO_APP_SECRET=" .env | cut -d'=' -f2)
        if [[ -z "$secret" ]]; then
          secret=$(grep -E "^APP_SECRET=" .env | cut -d'=' -f2)
        fi
    fi
    if [[ -z "$secret" ]]; then
        secret=$(grep -E "^APP_SECRET=" ../.env | cut -d'=' -f2)
    fi

    if [[ -n "$secret" ]]; then
        echo "Found APP_KEY and APP_SECRET."
        validate_key_and_secret "$key" "$secret"
        echo "Writing APP_KEY and APP_SECRET to current .env file..."
        echo "COBO_APP_KEY=$key" >> .env
        echo "COBO_APP_SECRET=$secret" >> .env
        return 0
    fi
    print_warning "APP_KEY or APP_SECRET not found."
    return 1
}
# %else
get_key_and_secret() {
    key=$(cobo --env "$1" config get app_key 2>/dev/null)
    secret=$(cobo --env "$1" config get api_secret 2>/dev/null)

    if [[ -n "$key" && -n "$secret" ]]; then
        print_success "Found API_KEY and API_SECRET from cobo config."
        read -p "Do you want to use this API_KEY ($key) and API_SECRET? (Y/n): " choice
        choice=${choice:-Y}
        case "$choice" in
            [Yy]* )
                validate_key_and_secret "$key" "$secret"
                echo "Writing API_KEY and API_SECRET to .env file..."
                echo "COBO_API_KEY=$key" >> .env
                echo "COBO_API_SECRET=$secret" >> .env
                return 0
                ;;
            * )
                print_warning "Skipping use of API_KEY and API_SECRET from cobo config."
                return 1
                ;;
        esac
    fi
    print_warning "API_KEY or API_SECRET not found."
    return 1
}
# %endif

# Function: Generate and store new secret
generate_and_store_secret() {
    # %if app_type == portal
    print_warning "Generating a new COBO_APP_SECRET..."
    cobo keys generate --force --key-type APP --file .env
    if [[ $? -eq 0 ]] && grep -q "^COBO_APP_SECRET=" .env && grep -q "^COBO_APP_KEY=" .env; then
        print_success "New COBO_APP_SECRET generated and saved to .env file."
        return 0
    fi
    print_error "Failed to generate COBO_APP_SECRET."
    return 1
    # %else
    print_warning "Generating a new COBO_API_SECRET..."
    cobo keys generate --force --key-type API --file .env
    if [[ $? -eq 0 ]] && grep -q "^COBO_API_SECRET=" .env && grep -q "^COBO_API_KEY=" .env; then
        print_success "New COBO_API_SECRET generated and saved to .env file."
        return 0
    fi
    print_error "Failed to generate COBO_API_SECRET."
    return 1
    # %endif
}

update_env_field() {
    local field_name=$1
    local value=$2

    # If the key exists, update its value
    if grep -q "^$field_name=" .env; then
        sed -i.bak "s/^$field_name=.*/$field_name=$value/" .env
        echo "Updated $field_name in .env to $value."
    else
        # If the key does not exist, add it
        echo "$field_name=$value" >> .env
        echo "Added $field_name=$value to .env."
    fi
}

generate_placeholders() {
    echo "Ensuring placeholders in .env file..."
    [[ -f ".env" ]] || touch .env

    # %if app_type == portal
    update_env_field "COBO_APP_KEY" ""
    update_env_field "COBO_APP_SECRET" ""
    # %else
    update_env_field "COBO_API_KEY" ""
    update_env_field "COBO_API_SECRET" ""
    # %endif

    print_success ".env file is up to date with required placeholders."
}

set_env_field() {
    local env=$1
    update_env_field "COBO_ENV" "$env"
}

# %if app_type == portal
set_client_id() {
    local env=$1
    local client_id

    if [[ "$env" == "prod" ]]; then
        client_id=$(cobo app manifest -k client_id 2>/dev/null)
    else
        client_id=$(cobo app manifest -k dev_client_id 2>/dev/null)
    fi

    if [[ -z "$client_id" || "$client_id" == *"-"* ]]; then
        print_warning "Failed to retrieve client ID from manifest. Using default placeholder."
        client_id="your-client-id-from-app-manifest"
    fi

    update_env_field "COBO_APP_CLIENT_ID" "$client_id"
}

generate_secret_key_if_needed() {
    if grep -q "^SECRET_KEY=" .env; then
        print_success "SECRET_KEY already exists in .env file."
        return 0
    fi

    read -p "SECRET_KEY is missing. Do you want to generate one? (Y/n): " choice
    choice=${choice:-Y}

    if [[ "$choice" =~ ^[Yy]$ ]]; then
        local secret_key
        secret_key=$(openssl rand -hex 32)
        update_env_field "SECRET_KEY" "$secret_key"
        print_success "Generated and added SECRET_KEY to .env file."
    else
        print_warning "SECRET_KEY was not generated. You can manually create one later with the following command:"
        print_warning "openssl rand -hex 32"
        update_env_field "SECRET_KEY" ""
    fi
}
# %endif


# Function: Ensure key and secret
ensure_key_and_secret() {
    # Generate COBO_ENV
    set_env_field "$1"

    # %if app_type == portal
    # Generate COBO_APP_CLIENT_ID and SECRET_KEY
    set_client_id "$1"
    generate_secret_key_if_needed
    # %endif

    # Check if key and secret exist in .env
    if check_env_file; then
        return 0
    fi

    # Fetch key and secret
    if get_key_and_secret "$1"; then
        return 0
    fi

    # Generate new key and secret if still missing
    read -p "Key and secret not found. Do you want to generate new ones? (Y/n): " choice
    choice=${choice:-Y}
    if [[ "$choice" =~ ^[Yy] ]]; then
        generate_and_store_secret
    else
        generate_placeholders
    fi
}
