import "jsr:@std/dotenv/load";
// @deno-types="npm:@types/express@5"
import express from "npm:express@5.1.0";
// @deno-types="npm:@types/cors@2.8.17"
import cors from "npm:cors@2.8.5";
import "https://deno.land/x/lodash@4.17.19/dist/lodash.js";
import { crypto } from "@std/crypto/crypto";
import { encodeHex } from "jsr:@std/encoding/hex";
import type { PrintRequest } from "./types.ts";

// import { getPython } from "jsr:@orgsoft/py";
// const { python } = await getPython();

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

function reject(res: express.Response, reason: string = "Invalid API Key") {
  res.status(403).send({
    status: "failure",
    d: { error: reason },
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

  console.log("Received print request:", printRequest);

  const command = new Deno.Command('/home/tater/.local/bin/uv', {
    args: [`run`, 'print.py', `${JSON.stringify(printRequest)}`],
  });
  const { code, stdout, stderr } = await command.output();
  console.log(new TextDecoder().decode(stdout));

  if (stderr.length > 0) {
    console.error("Error executing command:", new TextDecoder().decode(stderr));
    res.status(500).send({
      status: "failure",
      d: { error: "Failed to execute print command" },
    });
    return;
  }

  res.status(200).send({ status: "success", d: { 'success': true } });
});

app.listen(port, () => {
  console.log(`Listening on ${port} ...`);
});
