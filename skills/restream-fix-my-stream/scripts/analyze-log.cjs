#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const engine = require('./diagnostics.js');
try {
  const file=process.argv[2];
  if(!file)throw new Error('Usage: node analyze-log.cjs <OBS-log.txt>. Reads locally; prints evidence JSON; makes no network calls.');
  const stat=fs.statSync(file);
  if(!stat.isFile()||stat.size>8000000)throw new Error('Choose a regular UTF-8 log file under 8 MB and 2 million characters.');
  console.log(JSON.stringify(engine.parseLog(fs.readFileSync(file,'utf8')),null,2));
} catch(e) { console.error(e.message);process.exitCode=1; }
