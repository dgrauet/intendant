# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
