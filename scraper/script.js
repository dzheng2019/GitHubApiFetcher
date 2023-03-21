import * as fs from 'fs';
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({
  auth: "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",
});

let repos = []
let per_page = 10
let r = 500
let gap = 5
while (true) {
  let low = r
  let high = r + gap - 1
  let q = "filename:pre-commit-config.yaml size:" + low + ".." + high
  let resp = null;
  let att = 0;
  console.log('low ' + low + ' high ' + high)
  while (true) {
    try {
      resp = await octokit.rest.search.code({ q: q, per_page: per_page, page: 1 });
      break;
    } catch (error) {
      console.log("Failed inital. Attempt: " + att)
      att = att + 1
      await new Promise(r => setTimeout(r, 1000 * 100));
    }
  }
  let respData = resp.data
  repos = repos.concat(respData.items)
  if (respData.total_count == 0) {
    r = r + 10
    continue
  }
  let cur_sum = 0
  for (let i = 1; i < Math.floor(respData.total_count / per_page); i += 1) {
    console.log(repos.length)
    let newresp = null;
    let timeout = 1000 * 10;
    while (true) {
      try {
        newresp = await octokit.rest.search.code({ q: q, per_page: per_page, page: i + 1 });
        break;
      } catch (error) {
        console.log("Failed page. Attempt: " + att)
        att = att + 1
        await new Promise(r => setTimeout(r, timeout));
        timeout = timeout * 2
      }
    }
    repos = repos.concat(newresp.data.items)
    cur_sum = cur_sum + newresp.data.items.length
    if (cur_sum > 500) {
      break;
    }
    await new Promise(r => setTimeout(r, 2000));
  }

  let jsonContent = JSON.stringify(repos);
  let out_string = "./results_500/" + repos.length + ".json"
  fs.writeFile(out_string, jsonContent, 'utf8', function (err) {
    if (err) {
      return console.log(err);
    }
    console.log(out_string + " saved!");
  });

  r = r + gap
  if (repos.length > 40000) {
    console.log(r)
    break;
  }
}
