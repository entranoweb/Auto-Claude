#!/usr/bin/env node
/**
 * Morph Bridge for Auto Claude
 * Allows Python to call Morph SDK
 */

const { MorphClient } = require('@morphllm/morphsdk');

const method = process.argv[2];
const params = JSON.parse(process.argv[3]);

const morph = new MorphClient({ apiKey: process.env.MORPH_API_KEY });

(async () => {
  try {
    let result;
    
    if (method === 'fastApply') {
      result = await morph.fastApply.execute({
        target_filepath: params.target_filepath,
        instructions: params.instructions,
        code_edit: params.code_edit,
        baseDir: params.base_dir || '.'
      });
    } else if (method === 'warpGrep') {
      result = await morph.warpGrep.execute({
        query: params.query,
        repoRoot: params.repoRoot || '.',
        excludes: params.excludes,
        includes: params.includes
      });
    } else {
      throw new Error(`Unknown method: ${method}`);
    }
    
    console.log(JSON.stringify(result));
    process.exit(0);
    
  } catch (error) {
    console.error(JSON.stringify({ 
      success: false, 
      error: error.message,
      stack: error.stack
    }));
    process.exit(1);
  }
})();
