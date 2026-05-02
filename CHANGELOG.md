# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10](https://github.com/dgrauet/suzerain/compare/v0.1.9...v0.1.10) (2026-05-02)


### Features

* **adapters/python:** PK002 auto-fix runs sandboxed uv lock ([e5fc2d2](https://github.com/dgrauet/suzerain/commit/e5fc2d2cea47831a86277e315a071f5348145cb3))

## [0.1.9](https://github.com/dgrauet/suzerain/compare/v0.1.8...v0.1.9) (2026-05-02)


### Features

* **adapters/python:** add QU003 strict type-checker config rule ([99b3864](https://github.com/dgrauet/suzerain/commit/99b38644a39236a793ad2f82acda5335254f6afb))
* **checks:** add CI002 minimum CI steps rule ([92eff21](https://github.com/dgrauet/suzerain/commit/92eff217bd0d6f5880a24d3a63fea79c6bfc3cb4))
* **checks:** add CI003 commit message validation rule ([d55345d](https://github.com/dgrauet/suzerain/commit/d55345df20a5003a7b737cb993ea8b4f8c02ff00))
* **checks:** add LO003 docs/ directory rule (transverse) ([cc0e1b7](https://github.com/dgrauet/suzerain/commit/cc0e1b71e214f82697dcc87981494b64bfc6d7bc))
* **checks:** add RL004 strict SemVer rule ([c90ca5d](https://github.com/dgrauet/suzerain/commit/c90ca5de4d1164a809a384bdf4765553b4668a97))
* **checks:** add SA003 .env.example rule with safe auto-fix ([11be51e](https://github.com/dgrauet/suzerain/commit/11be51ed7f0f33286814627edb8ee770dbbb2cd6))
* **checks:** add TS002 regression_tests/ layout rule ([94775e2](https://github.com/dgrauet/suzerain/commit/94775e2a0cb0c4f4c49490e301aa225e1b45bad5))


### Bug Fixes

* **fixtures:** update conformant fixture and templates for new rules ([7548cd0](https://github.com/dgrauet/suzerain/commit/7548cd0000e7db168dbcce6eb7822e9ba672ee57))

## [0.1.8](https://github.com/dgrauet/suzerain/compare/v0.1.7...v0.1.8) (2026-05-02)


### Features

* **audit:** add dashboard_human formatter (A3 + legend) ([d6b5b14](https://github.com/dgrauet/suzerain/commit/d6b5b14ad65ba11e95cb88cdf068971998824cdf))
* **audit:** add dashboard_json formatter with schema_version=1 ([a3ead07](https://github.com/dgrauet/suzerain/commit/a3ead078738425a7bf9f8a375171c091f8948377))
* **audit:** add find_suzerain_repos for multi-repo discovery ([802cc19](https://github.com/dgrauet/suzerain/commit/802cc197b7ac5e70b06675035410fe411a454ac9))
* **checks:** DG005 requires both .gitignore and .gitattributes (2-pass fix) ([c8601ed](https://github.com/dgrauet/suzerain/commit/c8601ed0420b9ab951d9aa0545cd33889c4d07be))
* **commands:** add DashboardScan + scan helpers for dashboard command ([f54240d](https://github.com/dgrauet/suzerain/commit/f54240d77c8cecdbcbc137cd34dc2b3ad4829a2b))
* **commands:** add suzerain dashboard CLI command ([45a8669](https://github.com/dgrauet/suzerain/commit/45a8669182fb8ac7e595b8c79cb13d76b8e587d3))


### Bug Fixes

* **audit:** restore ✓/⚠ glyphs in dashboard_human per spec ([cc02d23](https://github.com/dgrauet/suzerain/commit/cc02d23d7909600592da1313e74aea80182bb72b))
* **tests:** silence ty invalid-assignment on intentional frozen test ([efaa434](https://github.com/dgrauet/suzerain/commit/efaa434cdaa03a673bd6a3e1eae53d7bd96c0084))


### Documentation

* redact local archive path references from public docs ([90e0def](https://github.com/dgrauet/suzerain/commit/90e0def8e74ba273f687d012af50a72b6219c1bf))
* redact remaining personal references from public files ([0c02a69](https://github.com/dgrauet/suzerain/commit/0c02a692cf18174cf1247d56c90103dbf3299c0a))
* translate handbook, ADRs, README, CLAUDE.md to English ([8342ddd](https://github.com/dgrauet/suzerain/commit/8342ddd6d98d505146979bcff6c824520bf3b985))
* update CLAUDE.md design reference for archived specs/plans ([dfa0100](https://github.com/dgrauet/suzerain/commit/dfa0100be7f530d20af17e8727f0293a3c29348b))

## [0.1.7](https://github.com/dgrauet/suzerain/compare/v0.1.6...v0.1.7) (2026-05-02)


### Features

* **audit:** register skill adapter in rule collector ([977fd15](https://github.com/dgrauet/suzerain/commit/977fd15ab9a4f9d9a41910341845d1fb6e163866))
* **core:** add CheckResult.skipped field for runtime preconditions ([7746c73](https://github.com/dgrauet/suzerain/commit/7746c73a77ab34bcaa8d36d7372845f8dbc8b438))
* **core:** detect skill stack with precedence over python ([f3066a8](https://github.com/dgrauet/suzerain/commit/f3066a887426954b390661dbafe0a0afb6b69d4b))
* **skill:** add find_skill_md inspector (depth limit + exclusions) ([bb62492](https://github.com/dgrauet/suzerain/commit/bb62492547d59e4cfca5e62908cbc4ab0f52bf71))
* **skill:** add parse_frontmatter inspector with BOM handling ([131788b](https://github.com/dgrauet/suzerain/commit/131788b181f75bca6d25b1e784d924ffb50e66b2))
* **skill:** add SK001 SKILL.md presence rule ([b1f2926](https://github.com/dgrauet/suzerain/commit/b1f2926f38af72c94eca3466e3d453ad98e7a5bb))
* **skill:** add SK002 frontmatter validity rule ([289decc](https://github.com/dgrauet/suzerain/commit/289deccc5ea1c21fa377b8a3c037a4c45b50f6d3))
* **skill:** add SK003 description length bounds rule ([67a5101](https://github.com/dgrauet/suzerain/commit/67a5101898ee5d343ca6a19023682dfd0fa1785d))
* **skill:** add SK004 name-matches-directory rule ([b3273cd](https://github.com/dgrauet/suzerain/commit/b3273cdccad9caa5f906db31a73c8aa3a4912b3c))
* **skill:** add SK005 evals/ presence rule ([8b0a87d](https://github.com/dgrauet/suzerain/commit/8b0a87d2f2ed6924588f4815841938ed885eef96))
* **skill:** add SK006 referenced dirs existence rule ([05cbb63](https://github.com/dgrauet/suzerain/commit/05cbb63dba79d7470372dcedb4033fb0dc4def8e))
* **skill:** add SK007 README install-path rule with safe fix ([a519271](https://github.com/dgrauet/suzerain/commit/a519271160c939e4f0b455071e685ed51ff50f85))
* **skill:** scaffold skill adapter package ([5933848](https://github.com/dgrauet/suzerain/commit/59338481f1378217b117686fcd5bf51133e9de28))


### Bug Fixes

* **skill:** tighten SK006 path regex + add missing SK003 skip test ([5f0a3c3](https://github.com/dgrauet/suzerain/commit/5f0a3c336aa6c424ac3921426df0942ed957424a))


### Documentation

* **core:** list "skill" in Repo.stack type comment ([fd63904](https://github.com/dgrauet/suzerain/commit/fd63904e6c61bd3a4297092b059fa998bece06a9))
* **handbook:** add 09-skill.md with SK001-SK007 entries ([7c020a5](https://github.com/dgrauet/suzerain/commit/7c020a5c66d807e8721d7684156849420daeed4c))

## [0.1.6](https://github.com/dgrauet/suzerain/compare/v0.1.5...v0.1.6) (2026-05-01)


### Features

* **adapters/python:** add QU004 ty-check rule (palier 2.7) ([295fd51](https://github.com/dgrauet/suzerain/commit/295fd51e1b13042a330be17e2139c92251297ce8))

## [0.1.5](https://github.com/dgrauet/suzerain/compare/v0.1.4...v0.1.5) (2026-05-01)


### Features

* **checks:** add .fix() for SA001/SA002/RL003 (palier 2.6) ([1ae0d66](https://github.com/dgrauet/suzerain/commit/1ae0d663e7eb33a90865bf9035cae955312cf140))

## [0.1.4](https://github.com/dgrauet/suzerain/compare/v0.1.3...v0.1.4) (2026-05-01)


### Bug Fixes

* **scaffold:** add placeholder test to avoid pytest exit 5 on fresh scaffolds ([2dc204d](https://github.com/dgrauet/suzerain/commit/2dc204defb3e1b33bc21154b660e57823ffd9b52))

## [0.1.3](https://github.com/dgrauet/suzerain/compare/v0.1.2...v0.1.3) (2026-05-01)


### Features

* **rules:** palier 2.5 — 7 new rules (DG002, SA002, SA004, RL003, CI004, PK004, TS003) ([8e0fca0](https://github.com/dgrauet/suzerain/commit/8e0fca0379184414b9a1f540119d20b8809443de))

## [0.1.2](https://github.com/dgrauet/suzerain/compare/v0.1.1...v0.1.2) (2026-05-01)


### Features

* **cli:** add 'suzerain new' scaffolder command ([5204cf7](https://github.com/dgrauet/suzerain/commit/5204cf7feba3ef95ac732590e057e6c9a67e3389))
* **scaffold:** add engine for copying + substituting templates ([488fec9](https://github.com/dgrauet/suzerain/commit/488fec9ad3b1f727a804d7ec0d17e91601a0af66))
* **scaffold:** add substitutions module with placeholder resolver ([07b25f2](https://github.com/dgrauet/suzerain/commit/07b25f2074e79b1bd820db3411d6575a0e472cb3))
* **templates:** add baseline ADR-0000 template for new repos ([beabb49](https://github.com/dgrauet/suzerain/commit/beabb496e03352e063c77f3857a13efdbc6f3cdf))


### Bug Fixes

* **cli:** inject git committer fallback for fresh environments ([475de6a](https://github.com/dgrauet/suzerain/commit/475de6a66382ce87d369b1f160a934aaee9a7547))


### Documentation

* document 'suzerain new' in README quickstart and roadmap ([72069c5](https://github.com/dgrauet/suzerain/commit/72069c505b9b7156427f91c745c96f180dbe59cd))
* update README for v0.1.1 (paliers 1+2 shipped, full CLI surface) ([6362146](https://github.com/dgrauet/suzerain/commit/636214628d0ae24de4b2d281a523fb03c696da52))

## [0.1.1](https://github.com/dgrauet/suzerain/compare/v0.1.0...v0.1.1) (2026-04-30)


### Features

* **adapters/python:** add inspectors (pyproject helpers) ([45df7e8](https://github.com/dgrauet/suzerain/commit/45df7e8eb8192ddaf641ffd0b9d394345993c2b7))
* **adapters/python:** add LO rules (LO001 src layout, LO002 tests at root) ([0a51576](https://github.com/dgrauet/suzerain/commit/0a515764b278280c627344d06375928e564a2b38))
* **adapters/python:** add PK rules (PK001-003) ([e633075](https://github.com/dgrauet/suzerain/commit/e6330756e7d1ca2f4c1d7b4676f6c0fd4bbac23f))
* **adapters/python:** add PK003.fix() to auto-create .python-version ([3917b5f](https://github.com/dgrauet/suzerain/commit/3917b5f7bf571f4f3a04509f314c19e29c1016d7))
* **adapters/python:** add QU rules (ruff, ty/pyright) ([c6de285](https://github.com/dgrauet/suzerain/commit/c6de2852ef74e38dcbc33e2e3d079e8ef99a81d1))
* **adapters/python:** add TS001 (pytest configured) ([9651ee2](https://github.com/dgrauet/suzerain/commit/9651ee2f0f77cf7c94de6bd7e4f20fc305f26483))
* **audit:** add --fix with safe/proposed boundary ([2a7e858](https://github.com/dgrauet/suzerain/commit/2a7e858ea5c4cabafe08c5d4af18c46986e8d506))
* **audit:** add human/json/markdown output formatters ([292182d](https://github.com/dgrauet/suzerain/commit/292182d4ec38b1046ef27135eb42b3de7a6c71a3))
* **audit:** add rule registry with stack and mode filtering ([a47e557](https://github.com/dgrauet/suzerain/commit/a47e557777c348e2533f48614026ab55d4713372))
* **audit:** add synchronous audit runner ([07d5f59](https://github.com/dgrauet/suzerain/commit/07d5f593628ac761c8f560da949cdefd1257a102))
* **checks:** add CI001 (CI workflow exists) ([756813c](https://github.com/dgrauet/suzerain/commit/756813c1eb5f82102450f9d2eb644f6960268ee7))
* **checks:** add DG transverse rules (DG001, DG003, DG004, DG005) ([24a53b2](https://github.com/dgrauet/suzerain/commit/24a53b21249203fab7fb14243aeedd10d0d0e9e6))
* **checks:** add RL transverse rules (RL001, RL002) ([ab8cf86](https://github.com/dgrauet/suzerain/commit/ab8cf8671c4e5062ee3bf4b1baf253292d184286))
* **checks:** add SA001 (pre-commit baseline) ([8a598e1](https://github.com/dgrauet/suzerain/commit/8a598e1b3c4a0015b07adfa04a04f36c4f2730aa))
* **cli:** add 'suzerain audit' command with multi-format output ([5f8cd5e](https://github.com/dgrauet/suzerain/commit/5f8cd5e3960f81f196b5917e0f361c92a470135f))
* **cli:** add 'suzerain doctor' command ([9119887](https://github.com/dgrauet/suzerain/commit/9119887f80abd847fb64034737ffac4b9b088a41))
* **cli:** add 'suzerain explain' command ([a51c19f](https://github.com/dgrauet/suzerain/commit/a51c19fe8edd3328ef55b684a7cafe7179a0b3c7))
* **cli:** add 'suzerain init' command ([dcc1bed](https://github.com/dgrauet/suzerain/commit/dcc1bed52d64640353b5ddde63c33126d0ad7428))
* **cli:** add typer entrypoint with --version flag ([defce03](https://github.com/dgrauet/suzerain/commit/defce033eade7dfa17767ba3ffa605a131849c16))
* **core:** add Finding and Report with weighted score ([7b4469e](https://github.com/dgrauet/suzerain/commit/7b4469e1266e63f211d9a5305d7db361e30cc725))
* **core:** add Handbook loader with rule + ADR parsing ([7276d21](https://github.com/dgrauet/suzerain/commit/7276d219daf58872053c8efecbb534539fe1213c))
* **core:** add Patch with safe-apply primitives ([bb887b0](https://github.com/dgrauet/suzerain/commit/bb887b04e52d460d82322bd854c14ce40d144486))
* **core:** add Repo and detect_stack ([c3888af](https://github.com/dgrauet/suzerain/commit/c3888af4b37c972c3152925fafbe3936fe2254e5))
* **core:** add Rule ABC and CheckResult ([c90c005](https://github.com/dgrauet/suzerain/commit/c90c00508ef8556f4b1943e1b12236c59a640c57))
* **core:** add SuzerainConfig with exemption parsing ([6058cf5](https://github.com/dgrauet/suzerain/commit/6058cf5e608653d08978ee26f8a9a1bf49f48c68))
* **templates:** add _common templates (ADR, CLAUDE.md, README, LICENSE, etc.) ([68b4d3e](https://github.com/dgrauet/suzerain/commit/68b4d3ecebce08a538e210bc0e9630cb6326f3ba))
* **templates:** add github/, python/ and node/ templates ([85ec2c5](https://github.com/dgrauet/suzerain/commit/85ec2c569d639f85008768b79928851c0dd4caa9))


### Bug Fixes

* **audit:** use Sequence[Rule] for covariant parameters (ty) ([0b238e3](https://github.com/dgrauet/suzerain/commit/0b238e3985b223ac9cc622c45eac93f59e5fd2dd))
* **checks:** RL002 accepts any lowercase CC type (per spec 1.0) ([9ac5f1e](https://github.com/dgrauet/suzerain/commit/9ac5f1eb367958a6b86015fe804240bb0b09d49e))
* **cli:** escape [exemptions] in init's Rich markup output ([6950d5c](https://github.com/dgrauet/suzerain/commit/6950d5c3d30ed54809773992209e0fc4be77aa23))
* **core:** make RuleSection.stacks immutable tuple ([ec61f6f](https://github.com/dgrauet/suzerain/commit/ec61f6f16750e7c8e695b7e6c10bded8341773fe))
* **tests:** narrow Optional dict before subscripting (ty) ([40e7f1b](https://github.com/dgrauet/suzerain/commit/40e7f1bf01f79ee5e40b249c136e8a86ce29e799))


### Documentation

* **adr:** add palier 1 ADRs 0000-0006 ([a79f056](https://github.com/dgrauet/suzerain/commit/a79f056c42ca8a36c2bd46b19af3b0a6679d6354))
* **handbook:** add palier 1 handbook (8 domains, 30 rules) ([38f66ca](https://github.com/dgrauet/suzerain/commit/38f66ca6935c879016bec05339e121f8ae9d6778))

## [Unreleased]

### Added
- Initial palier 1 scaffolding (handbook, ADRs, `init` and `explain` commands).
