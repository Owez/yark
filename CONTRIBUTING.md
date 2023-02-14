# Table of Contents

- [Table of Contents](#table-of-contents)
- [Contributing to Yark](#contributing-to-yark)
  - [Don't know coding?](#dont-know-coding)
  - [Want to code?](#want-to-code)
- [Internal Information](#internal-information)
  - [Setting up development](#setting-up-development)
  - [Ideology](#ideology)
    - [Users](#users)
    - [KISS](#kiss)
    - [Dependencies](#dependencies)
  - [Structure](#structure)
  - [Conventions](#conventions)
    - [Branches](#branches)
    - [To/from archives](#tofrom-archives)

# Contributing to Yark

## Don't know coding?

Contributing to Yark is easy and you can help out a ton without knowing how to code. If you've found a bug, just open an issue and describe your issue and show us the steps you went through to get it. We're happy to help :)

## Want to code?

If you know how to code and would like to make changes to Yark directly, you can either:

-  Open an issue explaining what you're changing (is it a feature or bug) and generally give some info and examples of it's intention, then submit a PR which closes the issue
-  Just submit a PR if it's a tiny change

Please make sure you describe the change so any developer could understand it – it could be a sentence or a nice big description. Aside from that, just follow the internal conventions set out below.

# Internal Information

This section goes through some of the more complex internal information which will be useful if your making changes inside of Yark in a PR.

## Setting up development

Setting up a full development enviroment for Yark is made easy thanks to Makefiles. To setup your development enviroment, first make sure these three packages are installed:

- Make ([Tutorial](https://www.gnu.org/software/make/#download); `apt install make`)
- NPM ([Tutorial](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm/))
- Python 3.11 ([Tutorial](https://www.python.org/downloads/); `apt install python3.11`)
- Poetry ([Tutorial](https://python-poetry.org/docs/#installation); `pip3.11 install poetry`)

If you install what you don't have quickly, it should take about 5-10 mins. You now have everything you need to develop except for some setup for the API; please read it's guide. Once that's done, here is the list of the ways you can use to develop the sub-projects of Yark:

1. To develop the GUI and API, or just the GUI: `make dev`
2. To develop just the API: `cd yark-api && make dev`
3. To develop the core library, you just need an IDE

Basically the top-level directory has a Makefile in it, and each specific project also has it's own specific Makefile. These files install all dependencies for you and run a nice development server if `dev` is available for you to use.

This is the section to link new developers to so that they can setup their machine.

## Ideology

### Users

The point of Yark is to make it as simple as possible for people to make YouTube archives. If something makes it harder for users to download and use the application, it's discouraged. Ideally you could get your mum to double-click a program called Yark and download a YouTube channel without needing any help or any tutorials, it should be that easy.

### KISS

Try to make changes following the [KISS](https://en.wikipedia.org/wiki/KISS_principle) premise, readable code is better than fast code unless it impacts performance for the user.

### Dependencies

The current situation of having to download Python 3.9+ and maybe FFmpeg should be the maximum hurdle users need to download and use Yark. This is already quite a high bar for non-techy users; ideally all of this should be a self-contained package.[^selfc]

Dependencies inside of the actual Yark code are a bit of a different story. If a dependency makes life a lot easier and the dependency is popular, it's probably worth using. Yark shouldn't have a hundred dependencies but if the extra download time and the security impact[^depsec] is worth it, then go for it.

[^selfc]: Like the example given in [Users](#users) before

[^depsec]: Every dependency is a new [attack vector](https://en.wikipedia.org/wiki/Attack_vector) waiting to be exploited

## Structure

Yark is separated into three areas of concern:

1. The core `yark` library which contains the underlying archiving logic
   - *This needs Python + Poetry to develop on*
2. The `yark-pages` project which contains the typical GUI users use
   - *This needs NPM + Python + Poetry to develop on*
3. The `yark-api` project which contains the behind-the-scenes API
   - *This needs Python + Poetry to develop on*
4. The `yark-cli` project which contains an old CLI interface
   - *This needs Python + Poetry to develop on*

When Yark is built into the app, it uses the `yark` library so all the logic works and builds the webpages from `yark-pages` for the [SvelteKit](https://kit.svelte.dev/)-based GUI. The app itself contains an API which these webpages connect to.

## Conventions

### Branches

The convention for branches/tags are:

1. The `master` branch acts as a mostly stable cutting-edge snapshot of features yet to be released. Think of this as a rolling release which might have a few bugs.
2. The `x.x-support` branches which are long-term patch/support branches for older versions which are kept alive until support is stopped for them.
3. Development branches are "feature branches", also known as the branches which have PRs for them. These get squash-merged into `master` so that `master` has a nice history.
4. Each release is also tagged with `vx.x` – e.g., `v1.3` or `v1.2.4`.

### To/from archives

Every time an archive is committed to a file or loaded back up from one, Yark needs to convert all of the rich classes to plain JSON objects so we can store it inside of the archive format. There are a few names that you'll see all the time because of this:

- `_from_archive_o`: Converts a whole JSON object in the archive to a whole class
- `_to_archive_o`: Converts a whole class to a single JSON object
- `_from_archive_ib`: Converts the ID of a JSON object and it's body to a class
- `_to_archive_b`: Converts a class to the body of a JSON object

As you can see, there are two categories of these conversions. We have full JSON "object" conversions, and those which have a separation of it's ID and it's body. As an example, this JSON object would use `_from_archive_o` and `_to_archive_o` for conversion:

```json
{
    "id": "4d8ad3a7-48f3-44ad-863f-a3214ccb0f40",
    "info": "some info here",
    "importance": 2
}
```

Whereas the `_b` and `_ib` ones would be used for a JSON child object which would look like this:

```json
"4d8ad3a7-48f3-44ad-863f-a3214ccb0f40": {
    "info": "some info here",
    "importance": 2
}
```

These two are used because the full objects (the first example) is easier to implement and are more self-contained, but we often need to select items by their ID straight from their parents.

This system will be changed to dataclasses soon (see [#107](https://github.com/Owez/yark/pull/107)) because it's not a good way to this. But for now this is what the archival conversion system looks like.
