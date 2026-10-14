# P2 HUB75 LED Matrix Driver - How to contribute
Propeller 2 Object for driving HUB75 LED Matrix panel sets

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

### Pages: [README](README.md) | [Hardware Turn-on](HardwareTurnon.md) | [Driver Details](THEOPS.md) | [Configuration Guide](DOCs/WiringGuide.md) | [Change Log](ChangeLog.md)

On this Page:

- [How to Contribute](#how-to-contribute) - the two ways to help
- [How to make a clean pull request](#how-to-make-a-clean-pull-request) - the steps, from fork to merge

Additional pages:

- [README](README.md) - Project overview, supported chips and configuration
- [Driver Details](THEOPS.md) - The driver's files, glossary and internals
- [Testing and Measurement](DOCs/TestingAndMeasurement.md) - The test programs and what each prints

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. The steps are below.

If you want to contribute to our project and make it better, your help is very welcome. Contributing is also a great way to learn more about social coding on Github, new technologies and their ecosystems and how to make constructive, helpful bug reports, feature requests and the noblest of all contributions: a good, clean pull request.

### How to make a clean pull request

- Create a personal fork of this project on Github.
- Clone the fork on your local machine. Your remote repo on Github is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.
- Create a new branch to work on! Branch from `develop` if it exists, else from `main`.
- Implement/fix your feature, comment your code.
- Follow the code style of the project, including indentation.
- Compile every demo and test top file (`demo_hub75_*.spin2`, `test_hub75_*.spin2`, `isp_hub75_anlyCheck.spin2`) with no warnings. The `test_hub75_*` programs are self-tests; run the ones your change touches (`test_hub75_converter` and `test_hub75_cube_fold` need no panels attached; what each prints is on the [Testing and Measurement](DOCs/TestingAndMeasurement.md) page).
- Write or adapt tests as needed.
- Add or change the documentation as needed.
- Squash your commits into a single commit with git's [interactive rebase](https://help.github.com/articles/interactive-rebase). Create a new branch if necessary.
- Push your branch to your fork on Github, the remote `origin`.
- From your fork open a pull request in the correct branch. Target the project's `develop` branch if there is one, else go for `main`!
- If the maintainer requests further changes just push them to your branch. The PR will be updated automatically.
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete
your extra branch(es).

And last but not least: Always write your commit messages in the present tense. Your commit message should describe what the commit, when applied, does to the code - not what you did to the code.

*(Special Thanks to [Marc Diethelm](https://github.com/MarcDiethelm) for this initial content for this page.)*

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
