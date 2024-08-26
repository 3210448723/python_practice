// ==UserScript==
// @name         CSUCAAutoLogin
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  �Զ���¼�����ϴ�ѧͳһ�����֤ƽ̨���ͺ�ű�
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
            // ���������ѧ��
            usernameInput.value = '244712254';
        }

        if (passwordInput) {
            // �������������
            passwordInput.value = 'zhaoyjm2002114*';
        }

        if (rememberMeCheckbox) {
            // ��ѡ7�����¼
            rememberMeCheckbox.checked = true;
        }

        // �����¼��ť
        var xpath = '//*[@id="login_submit"]';
        var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (matchingElement) {
            matchingElement.click();
        }
    };
})();