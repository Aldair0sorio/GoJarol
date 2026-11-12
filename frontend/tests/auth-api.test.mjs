import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { build } from 'vite';
const root = fileURLToPath(new URL('../', import.meta.url));
const output = await mkdtemp(join(tmpdir(), 'gojarol-auth-test-'));
await build({ configFile: false, root, logLevel: 'silent', build: {
  ssr: resolve(root, 'src/services/api.ts'), outDir: output,
  rollupOptions: { output: { entryFileNames: 'api.mjs' } },
} });
const { apiService, isBackendToken, verifyEmail, resendVerification } = await import(pathToFileURL(join(output,'api.mjs')).href);
const storage = new Map();
globalThis.localStorage = { getItem: key => storage.get(key) ?? null, setItem: (key,value) => storage.set(key,value), removeItem: key => storage.delete(key) };
after(async () => { await rm(output, { recursive: true }); });
const payload = { credential: 'google-id-token', role: 'student', nivel: 'secundaria', grado: 1 };
for (const status of [400,401,409,500,503]) {
  test(`Google HTTP ${status} never creates a simulated session`, async () => {
    storage.clear(); globalThis.fetch = async () => new Response(JSON.stringify({error:{message:'Rejected'}}),{status});
    const result = await apiService.loginWithGoogle(payload);
    assert.equal(result.success,false); assert.equal(result.token,undefined); assert.equal(result.user,undefined);
    assert.equal(storage.has('jarol_token'),false); assert.equal(storage.has('jarol_current_user'),false);
  });
}

test('Registration accepts verification pending without creating a session', async () => {
  storage.clear();
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/v1/auth/register/');
    const body = JSON.parse(options.body);
    assert.equal(body.full_name, 'Ana López'); assert.equal(body.password_confirm, 'test-only');
    assert.equal(body.estado, '30'); assert.equal(body.school, undefined); assert.equal(body.email_status, undefined);
    return new Response(JSON.stringify({verification_required:true,email_sent:true}), {status:201});
  };
  const result=await apiService.register({username:'ana',email:'ana@example.test',fullName:'Ana López',password:'test-only',passwordConfirm:'test-only',role:'student',estado:'30',nivel:'secundaria',grado:1});
  assert.equal(result.success,true);assert.equal(result.verificationRequired,true);assert.equal(result.emailSent,true);
  assert.equal(result.token,undefined);assert.equal(result.user,undefined);assert.equal(storage.size,0);
});

test('SMTP failure reports saved account without claiming delivery or creating session', async () => {
  storage.clear();
  globalThis.fetch=async () => new Response(JSON.stringify({account_created:true,email_sent:false,error:{message:'Delivery failed'}}),{status:503});
  const result=await apiService.register({username:'ana',email:'ana@example.test',fullName:'Ana',password:'test-only',passwordConfirm:'test-only',role:'student',estado:'30'});
  assert.equal(result.success,false);assert.equal(result.verificationRequired,true);assert.equal(result.emailSent,false);
  assert.equal(result.error,'Delivery failed');assert.equal(storage.size,0);
});

test('Pending login is distinct from an authenticated session', async () => {
  storage.clear();
  globalThis.fetch=async () => new Response(JSON.stringify({verification_required:true,error:{message:'Verify email'}}),{status:403});
  const result=await apiService.login({username:'ana',password:'test-only'});
  assert.equal(result.success,false);assert.equal(result.verificationRequired,true);assert.equal(storage.size,0);
});

test('Verification and resend errors propagate without writing session state', async () => {
  storage.clear();
  for (const status of [400,429,503]) {
    globalThis.fetch=async () => new Response(JSON.stringify({error:{message:'Rejected'}}),{status});
    await assert.rejects(verifyEmail('1','invalid'), error => error.status===status);
    await assert.rejects(resendVerification('ana@example.test'), error => error.status===status);
    assert.equal(storage.size,0);
  }
});
test('Network and malformed success responses fail closed', async () => {
  for (const fetch of [async () => { throw Error('offline'); }, async () => new Response('invalid-json'), async () => new Response(JSON.stringify({user:{id:1,rol:'estudiante'}})), async () => new Response(JSON.stringify({token:'jarol_gtoken_fake',user:{id:1,rol:'estudiante'}}))]) {
    storage.clear(); globalThis.fetch=fetch;
    const result=await apiService.loginWithGoogle(payload);
    assert.equal(result.success,false); assert.equal(result.user,undefined); assert.equal(storage.size,0);
  }
});
test('Verified backend response alone supplies identity and token', async () => {
  storage.clear();
  globalThis.fetch=async (url, options) => {
    assert.equal(url,'/api/v1/auth/google/');
    const body=JSON.parse(options.body);
    assert.equal(body.credential,payload.credential);
    assert.equal(body.email,undefined); assert.equal(body.name,undefined); assert.equal(body.picture,undefined);
    return new Response(JSON.stringify({token:'a'.repeat(40),user:{id:7,username:'server-user',email:'server@example.test',first_name:'Ana',last_name:'Pérez',rol:'docente',nivel:'',grado:null,xp:0,streak_days:0}}));
  };
  const result=await apiService.loginWithGoogle(payload);
  assert.equal(result.success,true); assert.equal(result.user.name,'Ana Pérez'); assert.equal(result.user.role,'teacher');
  assert.equal(result.user.email,'server@example.test');
});
test('Simulated or missing tokens cannot be accepted by AuthContext login guard', () => {
  for (const token of [undefined, '', 'jarol_demo_123','jarol_gtoken_123','jarol_token_123']) assert.equal(isBackendToken(token),false);
  assert.equal(isBackendToken('b'.repeat(40)),true);
});

for (const method of ['login', 'register']) {
  const input={username:'test-user',password:'test-only',email:'client@example.test',fullName:'Client',passwordConfirm:'test-only',estado:'30',role:'student'};
  test(`${method} failures never persist credentials or fabricate identity`, async () => {
    for (const fetch of [async () => new Response('{}',{status:401}), async () => { throw Error('offline'); },
      async () => new Response('not-json'), async () => new Response(JSON.stringify({user:{id:1,rol:'estudiante'}})),
      async () => new Response(JSON.stringify({token:'jarol_demo_fake',user:{id:1,rol:'estudiante'}}))]) {
      storage.clear();globalThis.fetch=fetch;
      const result=await apiService[method](input);
      assert.equal(result.success,false);assert.equal(result.user,undefined);assert.equal(storage.size,0);
    }
  });
  if (method === 'login') test(`${method} preserves the backend identity and administrator role`, async () => {
    storage.clear();
    globalThis.fetch=async () => new Response(JSON.stringify({token:'c'.repeat(40),user:{id:9,username:'real-admin',email:'server@example.test',rol:'admin',xp:0,streak_days:0}}));
    const result=await apiService[method](input);
    assert.equal(result.success,true);assert.equal(result.user.role,'admin');assert.equal(result.user.email,'server@example.test');
    assert.equal(storage.get('jarol_token'),'c'.repeat(40));
  });
}
