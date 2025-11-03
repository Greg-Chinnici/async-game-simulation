output=$(openssl rand -hex 32)

echo $output >> .env
