# ACE2 GUI Development Guide

## Initial setup

This project has VSCode devcontainer support to ensure that anyone working on the project does so in a consistent environment as well as follows the same formatting/styling guidelines.

### Required setup

In order to work within the devcontainer, you will need the following installed on your system:
* [Docker](https://www.docker.com/products/docker-desktop)
* [VSCode](https://code.visualstudio.com/)
* [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) VSCode extension pack

NOTE: If you are developing in Windows, you will need to make sure that you have WSL 2 set up and properly configured with Docker. That is outside the scope of this documentation, but you can find steps [here](https://docs.docker.com/desktop/windows/wsl/).

### Optional setup

The end-to-end tests with Cypress can be executed within the devcontainer, but if you would like to use the Cypress Test Runner, you will also need to install [Node.js 16](https://nodejs.org/en/download/current/), as this needs to run outside of the devcontainer on your local system.

## Working in the VSCode devcontainer

When you open the project in VSCode, it will detect the devcontainer configuration and prompt you to reopen it inside of the container:

![Reopen in Container](open-in-container.png)

Once you choose the `Reopen in Container` option, VSCode will work on building the environment. Once it is complete, you can open a terminal within VSCode to interact with the application:

![Terminal](terminal.png)

Any work done on the application should be done through the devcontainer. If you make a change to the devcontainer configuration (found in the `.devcontainer` directory), you can rebuild the devcontainer by clicking on `Dev Container: ACE2 AMS GUI` in the lower-left corner of VSCode and then selecting the `Rebuild Container` option in the menu that opens.

## Managing NPM packages

You should not directly edit the dependencies or devDependencies inside of `package.json` or anything in `package-lock.json`. **Any changes to packages should be performed inside of the devcontainer via the `npm` command**:

### Install new dependency package

You would install a package like this if it is something the final compiled application needs:
```
npm install <package>
```

### Install new dev dependency package

You would install a package like this if it is only needed during development:
```
npm install -D <package>
```

### Uninstall package

You can uninstall/remove a package regardless of how it was installed by:
```
npm uninstall <package>
```

## Running tests

This application has a suite of unit tests performed by [Jest](https://jestjs.io/) and end-to-end tests performed by [Cypress](https://www.cypress.io/).

### Unit tests
You can execute the unit tests directly inside of the devcontainer:
```
npm run test:unit
```

### End-to-end tests
You can execute the end-to-end tests directly inside of the devcontainer:
```
npm run test:e2e
```

#### Test Runner

Cypress also comes with an amazing [Test Runner](https://docs.cypress.io/guides/core-concepts/test-runner) that lets you see and interact with the tests in your local web browser. This can be helpful when writing end-to-end tests to ensure they are working properly as well as any debugging you might need to do.

However, this will need to be performed on your local system ouside of the devcontainer. To do this, you will need to have Node.js 16 installed.

**Step 1:** Inside of the devcontainer, run the application so that it is available on port 8080:
```
npm run serve
```

**Step 2:** Outside of the devcontainer on your local system (but still inside of the project directory), open the Test Runner:
```
npx cypress open
```

![Test Runner](test-runner.png)

For more information on what you can do with the Test Runner, view the Test Runner [documentation](https://docs.cypress.io/guides/core-concepts/test-runner).