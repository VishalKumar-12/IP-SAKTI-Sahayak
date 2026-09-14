/* ==========================================================================
   auth.js — login / signup / session handling, shared across every page
   ========================================================================== */

(function () {
  'use strict';

  var API_BASE_URL = "http://127.0.0.1:5000/api";
  var TOKEN_KEY = "ipsakti_token";
  var USER_KEY = "ipsakti_user";


  /* ---------------- Session storage helpers ---------------- */

  function getToken() {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch (e) {
      return null;
    }
  }

  function getUser() {
    try {
      var raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setSession(token, user) {
    try {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch (e) { /* storage unavailable */ }
  }

  function clearSession() {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (e) { /* storage unavailable */ }
  }

  function isLoggedIn() {
    return !!getToken();
  }


  /* ---------------- API calls ---------------- */

  function signup(name, email, password) {
    return fetch(API_BASE_URL + "/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, email: email, password: password })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || "Unable to create account.");
          }
          setSession(data.token, data.user);
          return data.user;
        });
      });
  }

  function login(email, password) {
    return fetch(API_BASE_URL + "/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || "Unable to log in.");
          }
          setSession(data.token, data.user);
          return data.user;
        });
      });
  }

  function logout(redirectTo) {
    clearSession();
    window.location.href = redirectTo || getRelativePath("index.html");
  }


  /* ---------------- Path helpers ---------------- */

  function isInPagesFolder() {
    return window.location.pathname.indexOf("/pages/") !== -1;
  }

  function getRelativePath(target) {
    return isInPagesFolder() ? target : "pages/" + target;
  }


  /* ---------------- Route guard ---------------- */

  function requireAuth() {
    if (!isLoggedIn()) {
      var next = encodeURIComponent(window.location.pathname);
      window.location.href = getRelativePath("login.html") + "?next=" + next;
      return false;
    }
    return true;
  }


  /* ---------------- Nav rendering ---------------- */

  function renderNavAuth() {
    var navTools = document.getElementById("navTools");
    if (!navTools) return;

    var container = document.getElementById("authNav");
    if (!container) {
      container = document.createElement("div");
      container.id = "authNav";
      container.className = "auth-nav";
      navTools.appendChild(container);
    }

    container.innerHTML = "";

    var user = getUser();

    if (user && isLoggedIn()) {
      var greeting = document.createElement("span");
      greeting.className = "auth-nav-name";
      greeting.textContent = user.name;

      var logoutBtn = document.createElement("button");
      logoutBtn.type = "button";
      logoutBtn.className = "btn btn-outline btn-sm";
      logoutBtn.textContent = "Log out";
      logoutBtn.addEventListener("click", function () {
        logout(isInPagesFolder() ? "../index.html" : "index.html");
      });

      container.appendChild(greeting);
      container.appendChild(logoutBtn);
    } else {
      var loginLink = document.createElement("a");
      loginLink.className = "btn btn-outline btn-sm";
      loginLink.href = getRelativePath("login.html");
      loginLink.textContent = "Log in";

      var signupLink = document.createElement("a");
      signupLink.className = "btn btn-primary btn-sm";
      signupLink.href = getRelativePath("signup.html");
      signupLink.textContent = "Sign up";

      container.appendChild(loginLink);
      container.appendChild(signupLink);
    }
  }


  document.addEventListener("DOMContentLoaded", renderNavAuth);


  window.IPSaktiAuth = {
    signup: signup,
    login: login,
    logout: logout,
    getToken: getToken,
    getUser: getUser,
    isLoggedIn: isLoggedIn,
    requireAuth: requireAuth,
    renderNavAuth: renderNavAuth
  };

})();
