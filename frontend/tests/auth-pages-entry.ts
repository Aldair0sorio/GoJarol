import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../src/context/AuthContext';
import { LoginPage } from '../src/views/auth/LoginPage';
import { RegisterPage } from '../src/views/auth/RegisterPage';
import { VerificationPendingPage, VerifyEmailPage, VerificationInvalidPage, VerificationSuccessPage } from '../src/views/auth/VerificationPages';
export { routeRedirect, tabPaths } from '../src/routing';
export { STATES } from '../src/data/states';
export function renderPage(page: string) {
  const Component = { login: LoginPage, register: RegisterPage, pending: VerificationPendingPage,
    verify: VerifyEmailPage, invalid: VerificationInvalidPage, success: VerificationSuccessPage }[page];
  if (!Component) throw Error('Unknown test page');
  return renderToStaticMarkup(createElement(MemoryRouter, null,
    createElement(AuthProvider, null, createElement(Component))));
}
