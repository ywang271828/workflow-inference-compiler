// See https://docs.github.com/en/actions/creating-actions/creating-a-javascript-action
// NOTE: Every time you modify this file, you need to run
// `ncc build index.js && git add -f dist/index.js index.js package.json package-lock.json`
// You do NOT need to git add node_modules/*

const core = require('@actions/core');
const github = require('@actions/github');
const jsZip = require('jszip')
const fs = require('fs');

(async() => {
  try {
    const workflow_run_id = core.getInput('workflow_run_id');
    const repo_owner = core.getInput('repo_owner');
    const repo_name = core.getInput('repo_name');

    const allArtifacts = await github.rest.actions.listWorkflowRunArtifacts({
      owner: repo_owner,
      repo: repo_name,
      run_id: workflow_run_id,
    });

    const matchArtifact = allArtifacts.data.artifacts.filter((artifact) => {
      return artifact.name == "parameters"
    })[0];

    //const matchArtifact = allArtifacts.data.artifacts[0];

    const download = await github.rest.actions.downloadArtifact({
      owner: repo_owner,
      repo: repo_name,
      artifact_id: matchArtifact.id,
      archive_format: 'zip',
    });

    fs.writeFileSync("./parameters.zip", Buffer.from(download.data));
    var pr_payload = {};
    //const pr_payload = JSON.parse(download.data);
    
    jsZip.loadAsync("./parameters.zip").then(function (zip) {
      Object.keys(zip.files).forEach(function (filename) {
        zip.files[filename].async('string').then(function (fileData) {
          pr_payload = JSON.parse(fileData);
        })
      })
    });

    core.setOutput("event_name", pr_payload.event_name);
    core.setOutput("head_sha", pr_payload.head_sha);
    core.setOutput("sender_repo_owner", pr_payload.sender_repo_owner);
    core.setOutput("sender_repo_ref", pr_payload.sender_repo_ref);
    core.setOutput("sender_repo_name", pr_payload.sender_repo_name);

  } catch (error) {
    core.setFailed(error.message);
  }
}) ();
