build:
	git submodule update --init --recursive

lint:
	python3 scripts/lint_wiki.py wiki/

# graphify 산출물을 Pages 사이트로 빌드만 (git 미접촉)
graph-site:
	python3 scripts/deploy_graph_pages.py --out graphify-out/_site

# gh-pages 브랜치에 커밋 + push
deploy-graph:
	python3 scripts/deploy_graph_pages.py

.PHONY: build lint graph-site deploy-graph
