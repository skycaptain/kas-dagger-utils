// Kas Utils
//
// See https://semantic-release.gitbook.io/ for usage.
//
// SPDX-License-Identifier: BSD-3-Clause
//
// RELEASE BUSTER: 0
//

/** @type {import('semantic-release').GlobalConfig} */
export default {
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "semantic-release-pypi",
    [
      "@semantic-release/git",
      {
        assets: ["pyproject.toml"],
      },
    ],
    "@semantic-release/github",
  ],
  preset: "conventionalcommits",
};
