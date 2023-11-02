serve:
	@ docker compose up

serve_local:
	@ ./scripts/start_dev_server.sh

generate:
	@ mkdir -p ./docs
	@ cp -r ./assets ./docs/
	@ ./scripts/generate_site.sh

clean:
	@ rm -rf ./.grotsky
