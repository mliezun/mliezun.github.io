serve:
	@ ./scripts/start_dev_server.sh

generate:
	@ mkdir -p ./_site
	@ cp -r ./assets ./_site/
	@ ./scripts/generate_site.sh

clean:
	@ rm -rf ./.grotsky
	@ rm -rf ./_site

