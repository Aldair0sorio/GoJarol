import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { build } from 'vite';
import react from '@vitejs/plugin-react';
const root = fileURLToPath(new URL('../', import.meta.url));
const output = await mkdtemp(join(tmpdir(), 'gojarol-pages-test-'));
after(async () => { await rm(output, { recursive: true }); });
await build({ configFile:false,root,plugins:[react()],logLevel:'silent',ssr:{noExternal:true},
  build:{ssr:resolve(root,'tests/auth-pages-entry.ts'),outDir:output,rollupOptions:{output:{entryFileNames:'pages.mjs'}}} });
const {renderPage,routeRedirect,STATES} = await import(pathToFileURL(join(output,'pages.mjs')).href);

test('Guests are redirected away from every private route', () => {
  for (const path of ['/','/chat','/perfil','/clases','/panel','/alumnos','/progreso']) assert.equal(routeRedirect(path,false,'student'),'/login');
});
test('Authenticated entry and login always lead to the local chat', () => {
  for (const role of ['student','teacher','admin']) {
    for (const path of ['/','/login','/registro']) assert.equal(routeRedirect(path,true,role),'/chat');
    assert.equal(routeRedirect('/chat',true,role),null);
    assert.equal(routeRedirect('/perfil',true,role),null);
    assert.equal(routeRedirect('https://attacker.test',true,role),'/chat');
  }
});
test('Academic role routes stay isolated and destinations do not loop', () => {
  assert.equal(routeRedirect('/panel',true,'student'),'/chat');
  assert.equal(routeRedirect('/alumnos',true,'student'),'/chat');
  for (const role of ['teacher','admin']) {
    assert.equal(routeRedirect('/panel',true,role),null); assert.equal(routeRedirect('/alumnos',true,role),null);
    assert.equal(routeRedirect('/progreso',true,role),'/chat');
  }
  assert.equal(routeRedirect('/login',false,'student'),null);
});
test('Verification and recovery pages are reachable without a session', () => {
  for (const path of ['/verificacion-pendiente','/verificar-correo/1/token','/verificacion-exitosa','/verificacion-invalida','/recuperar-contrasena']) assert.equal(routeRedirect(path,false,'student'),null);
});
test('Registration renders the required student field order and all state choices', () => {
  const html=renderPage('register');
  const labels=['Nombre completo','Correo electrónico','Nombre de usuario','Nivel escolar','Año escolar','Estado de residencia','Contraseña','Confirmar contraseña'];
  let index=-1;
  for (const label of labels) { const next=html.indexOf(label,index+1);assert.ok(next>index,label);index=next; }
  assert.equal(STATES.length,32);assert.equal(new Set(STATES.map(([code])=>code)).size,32);
  for (const [code,name] of STATES) assert.ok(html.includes(`value="${code}">${name}</option>`));
  assert.ok(!html.includes('Escuela/Municipio'));assert.ok(!html.includes('role="dialog"'));
  assert.ok(html.includes('autoComplete="new-password"'));assert.ok(html.includes('aria-label="Mostrar contraseña"'));
});
test('Login has real navigation and no demonstration accounts', () => {
  const html=renderPage('login');
  for (const path of ['/registro','/recuperar-contrasena']) assert.ok(html.includes(`href="${path}"`));
  assert.ok(html.includes('autoComplete="current-password"'));assert.ok(!html.includes('jarol_demo'));
});
test('Verification states render meaningful headings and actions', () => {
  for (const page of ['pending','verify','invalid','success']) {
    const html=renderPage(page); assert.ok(html.includes('<h1')); assert.ok(!html.includes('role="dialog"'));
  }
});
