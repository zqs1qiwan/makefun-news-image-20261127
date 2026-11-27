// Entry point for the make.fun news-image-20261127 harness.
// Copies the pre-built entry.png into the harness output directory.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoDir = dirname(fileURLToPath(import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outputDir, { recursive: true });
copyFileSync(resolve(repoDir, "entry.png"), resolve(outputDir, "entry.png"));
