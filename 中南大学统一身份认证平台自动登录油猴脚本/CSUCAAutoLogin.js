// ==UserScript==
// @name         CSUCAAutoLogin
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  自动登录“中南大学统一身份认证平台”油猴脚本
// @author       YJM
// @match        https://ca.csu.edu.cn/authserver/login*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    window.onload = function() {
        // Fill the username and password
        var usernameInput = document.evaluate('//*[@id="username"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var passwordInput = document.evaluate('//*[@id="password"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var rememberMeCheckbox = document.evaluate('//*[@id="rememberMe"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

        if (usernameInput) {
            // 请输入你的学号
            usernameInput.value = '244712254';
        }

        if (passwordInput) {
            // 请输入你的密码
            passwordInput.value = 'zhaoyjm2002114*';
        }

        if (rememberMeCheckbox) {
            // 勾选7天免登录
            rememberMeCheckbox.checked = true;
        }

        // 点击登录按钮
        var xpath = '//*[@id="login_submit"]';
        var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (matchingElement) {
            matchingElement.click();
        }
    };
})();