// See https://docs.github.com/en/actions/creating-actions/creating-a-javascript-action
// NOTE: Every time you modify this file, you need to run
// `ncc build index.js && git add -f dist/index.js index.js package.json package-lock.json`
// You do NOT need to git add node_modules/*

const core = require('@actions/core');
const fs = require('fs');

try {
  const event_name = core.getInput('event_name');
  const head_sha = core.getInput('head_sha');
  const sender_repo_owner = core.getInput('sender_repo_owner');
  const sender_repo_ref = core.getInput('sender_repo_ref');
  const sender_repo_name = core.getInput('sender_repo_name');

  const pr_payload = {
    "event_name": event_name,
    "head_sha": head_sha,
    "sender_repo_owner": sender_repo_owner,
    "sender_repo_ref": sender_repo_ref,
    "sender_repo_name": sender_repo_name
  };

  fs.writeFileSync(`params.json`, Buffer.from(JSON.stringify(pr_payload)));

} catch (error) {
  core.setFailed(error.message);
}
