// ==UserScript==
// @name         CSUCAAutoLogin
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  自动登录“中南大学统一身份认证平台”及使用该平台鉴权的校内网页的油猴脚本
// @author       YJM
// @match        *://ca.csu.edu.cn/authserver/login*

// @match        *://mail.csu.edu.cn/
// @match        *://mail.csu.edu.cn/coremail/

// @match        *://libdb.csu.edu.cn/*
// @match        *://ehall.csu.edu.cn/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';
    // 如果是统一身份认证平台
    var ca = function () {
        // Fill the username and password
        let usernameInput = document.evaluate('//*[@id="username"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        let passwordInput = document.evaluate('//*[@id="password"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        let rememberMeCheckbox = document.evaluate('//*[@id="rememberMe"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

        if (usernameInput) {
            // 请输入你的学号
            usernameInput.value = 'xxx';
        }

        if (passwordInput) {
            // 请输入你的密码
            passwordInput.value = 'xxx';
        }

        if (rememberMeCheckbox) {
            // 勾选7天免登录
            rememberMeCheckbox.checked = true;
        }

        // 点击登录按钮
        let xpath = '//*[@id="login_submit"]';
        let matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (matchingElement) {
            matchingElement.click();
        } else {
            console.error('脚本未找到登录按钮！')
        }
    };
    // 如果是邮箱登录页面
    var mail = function () {
        // 点击统一身份认证登录按钮（如果已登录，由于没有篡改猴脚本匹配的url，因此不会执行）
        let xpath = '/html/body/div[3]/div[4]/div[3]/div[3]/div[1]/form/div[4]/button';
        let matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (matchingElement) {
            matchingElement.click();
        } else {
            console.error('脚本未找到统一身份认证登录按钮！')
        }
    };
    // 如果是图书馆页面
    var libdb = function () {
        let xpath = '/html/body/div[2]/div/div[1]/div/span[1]';
        let matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        // 如果不存在用户名（你好，），跳转到登录页面
        if (matchingElement == null) {
            window.location.href = 'http://libdb.csu.edu.cn/login';
        } else {
            console.log('已登录')
        }
    };
    // 如果是网上办事大厅页面
    var ehall = function () {
        // 已登录
        let username_xpath = '/html/body/div[1]/div[1]/div/div[3]/div';
        let matchingElement = document.evaluate(username_xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        // 如果不存在用户名，跳转到登录页面
        if (matchingElement == null) {
            let login_logout_xpath = '/html/body/div[1]/div[1]/div/div[3]/button';
            let matchingElement = document.evaluate(login_logout_xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (matchingElement) {
                matchingElement.click();
            } else {
                console.error('脚本未找到登录按钮！')
            }
        } else {
            console.log('已登录')
        }
    };

    if (window.location.href.indexOf('ca.csu.edu.cn/authserver/login') !== -1) {
        window.addEventListener('load', ca);
    } else if (window.location.href.indexOf('mail.csu.edu.cn') !== -1) {
        window.addEventListener('load', mail);
    } else if (window.location.href.indexOf('libdb.csu.edu.cn') !== -1) {
        window.addEventListener('load', libdb);
    } else if (window.location.href.indexOf('ehall.csu.edu.cn') !== -1) {
        window.addEventListener('load', ehall);
    }
})();
