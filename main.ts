import "jsr:@std/dotenv/load";
// @deno-types="npm:@types/express@5"
import express from "npm:express@5.1.0";
// @deno-types="npm:@types/cors@2.8.17"
import cors from "npm:cors@2.8.5";
import "https://deno.land/x/lodash@4.17.19/dist/lodash.js";
import { crypto } from "@std/crypto/crypto";
import { encodeHex } from "jsr:@std/encoding/hex";
import type { PrintRequest, UselessFact } from "./types.ts";

// now `_` is imported in the global variable, which in deno is `self`
// deno-lint-ignore no-explicit-any
const _ = (self as any)._; // Workaround to get lodash in Deno

const token = String(Deno.env.get("APP_TOKEN")) || "";

const app = express();
const port = Number(Deno.env.get("APP_PORT")) || 3000;
app.use(express.json());
app.use(cors());

async function hashTokenFromRequest(req: express.Request) {
  const passedKey = req.header("x-api-key") || "";
  const messageBuffer = new TextEncoder().encode(passedKey);
  const hashBuffer = await crypto.subtle.digest("SHA-256", messageBuffer);
  const hash = encodeHex(hashBuffer);
  return hash;
}

async function authenticateTokenInRequest(req: express.Request) {
  const hash = await hashTokenFromRequest(req);
  if (hash === token) {
    return true;
  } else {
    console.log("Invalid API Key: ", hash);
    return false;
  }
}

async function getFact() {
  const response = await fetch('https://uselessfacts.jsph.pl/api/v2/facts/random');
  const data: UselessFact = await response.json();
  return data;
}

function reject(res: express.Response, reason: string = "Invalid API Key") {
  res.status(403).send({
    status: "failure",
    d: { 'success': false, 'exit_code': 1, 'error': reason }
  });
  return;
}

app.get("/", async (req, res) => {
  if ((await authenticateTokenInRequest(req)) == false) {
    reject(res);
    return;
  }

  res.status(200).send("Hello World!");
});

app.post("/api/print", async (req, res) => {
  if ((await authenticateTokenInRequest(req)) == false) {
    reject(res, "Invalid API Key");
    return;
  }

  const printRequest: PrintRequest = req.body;
  const fact = await getFact();
  printRequest.fact = fact.text;

  console.log("Received print request:", printRequest);

  const command = new Deno.Command('/home/tater/.local/bin/uv', {
    args: [`run`, 'print.py', `${JSON.stringify(printRequest)}`],
  });
  const { code, stdout, stderr } = await command.output();

  if (code != 0) {
    // Wait for 5 seconds before retrying
    await new Promise(resolve => setTimeout(resolve, 5000));
    const retryCommand = new Deno.Command('/home/tater/.local/bin/uv', {
      args: [`run`, 'print.py', `${JSON.stringify(printRequest)}`],
    });
    const { code: retryCode, stdout: retryStdout, stderr: retryStderr } = await retryCommand.output();

    if (retryCode != 0) {
      res.status(500).send({
        status: "failure",
        d: { error: { 'success': false, 'exit_code': retryCode, 'error': new TextDecoder().decode(retryStderr) } },
      });
      return;
    }
  }

  res.status(200).send({ status: "success", d: { 'success': true, 'exit_code': code, 'error': 'none' } });
});

app.listen(port, () => {
  console.log(`Listening on ${port} ...`);
});
