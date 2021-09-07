serve:
	@ ./scripts/start_dev_server.sh

generate:
	@ mkdir -p ./docs
	@ cp -r ./assets ./docs/
	@ ./scripts/generate_site.sh

clean:
	@ rm -rf ./.grotsky

