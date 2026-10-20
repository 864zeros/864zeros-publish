#!/usr/bin/env node
/**
 * generate-kate-briefing.cjs
 * 864zeros Studio (864zeros-publish) | Powered by BRK-MEDIA-003 (agent-neural-avatar-pipeline.js)
 *
 * Generates reproducible Neural Avatar Briefing Jobs for Kate Zefore (COS-001) or any of the
 * 13 864zeros roster personas registered in shared/avatars/ROSTER_NEURAL_AVATAR_MANIFEST.json.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { buildNeuralAvatarJob } = require('C:\\dev\\864zeros-llc\\LLC-DIV-3-FACTORY\\shared\\bricks\\agent-neural-avatar-pipeline.js');

const MANIFEST_PATH = path.join(__dirname, '..', 'shared', 'avatars', 'ROSTER_NEURAL_AVATAR_MANIFEST.json');
const OUTPUT_QUEUE_PATH = path.join(__dirname, '..', 'shared', 'avatars', 'ACTIVE_BRIEFING_RENDER_QUEUE.json');

function generateBriefingQueue(customScript) {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
  const defaultScript =
    customScript ||
    'Good morning, Jeff — Kate here. All six overnight workstreams are complete, the 13-person neural avatar manifest is locked, and our 18 Google Workspace scenario storyboards and Episode 1 podcast script are vaulted in the Corporate Library.';

  const jobs = manifest.roster_avatars.map((persona) => {
    return buildNeuralAvatarJob({
      avatarId: persona.id,
      sourcePortraitPath: persona.stagePortrait || persona.sourcePortrait,
      scriptText: persona.id === 'kate-zefore' ? defaultScript : `${persona.name} (${persona.code}) reporting ready on station ${persona.homeRoom}.`,
      voiceModel: persona.voiceSpec.voiceModel,
      pitchHz: persona.voiceSpec.pitchHz,
      ratePct: persona.voiceSpec.ratePct,
      diffusionEngine: persona.diffusionEngine,
      outputDir: 'public/kate-live-rig',
      existingProtectedFiles: [persona.sourcePortrait, persona.stagePortrait].filter(Boolean)
    });
  });

  const queueDoc = {
    generated_at: new Date().toISOString(),
    brick_id: 'BRK-MEDIA-003',
    total_personas_ready: jobs.length,
    kate_morning_brief_job: jobs[0],
    roster_jobs: jobs
  };

  fs.writeFileSync(OUTPUT_QUEUE_PATH, JSON.stringify(queueDoc, null, 2), 'utf8');
  console.log(`[generate-kate-briefing] Generated ${jobs.length}/13 persona neural briefing jobs -> ${OUTPUT_QUEUE_PATH}`);
  return queueDoc;
}

if (require.main === module) {
  generateBriefingQueue(process.argv[2]);
}

module.exports = { generateBriefingQueue };
