/*
 * Author: Erick Ruh Cardozo (W1SD00M) - <erickruhcardozo1998@hotmail.com>
 * Date: May 1, 2022 - 3:05 PM
 * Last Modified: May 3, 2022
 */
chrome.runtime.onInstalled.addListener(function() {
  chrome.storage.local.set({enabled: true, key: ''});
});

chrome.webNavigation.onCompleted.addListener(async function () {
  let tab = await getCurrentTab();

  chrome.storage.local.get(['enabled', 'key'], (data) => {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: autoClickCode,
      args: [data.enabled, data.key]
    });
  });
}, { url: [{ pathContains: 'DoacaoDocumentoFiscalCadastrar' }] });

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (sender.id !== chrome.runtime.id) {
    return true;
  }
  
  switch (message.command) {
    case 'SET_AUTOCLICK_ENABLED':
      chrome.storage.local.set({enabled: true});
      chrome.tabs.reload();
      break;
      
      case 'SET_AUTOCLICK_DISABLED':
        chrome.storage.local.set({enabled: false});
        chrome.tabs.reload();
      break;

    case 'QUERY_AUTOCLICK_ENABLED':
      chrome.storage.local.get(['enabled'], (data)=> {
        sendResponse(data);
      });
      break;
      
    case 'SET_ACCESSKEY':
      chrome.storage.local.set({key: message.key});
      break;

    case 'QUERY_ACCESSKEY':
      chrome.storage.local.get(['key'], (data)=> {
        sendResponse(data);
      });
      break;
  }

  return true;
});

function autoClickCode(enabled, key) {
  const cnpjField = document.querySelector('#cnpjEntidade');
  const accessKeyField = document.querySelector('#chaveAcesso');
  const donateNoteButton = document.querySelector('#btnDoarDocumento');

  cnpjField.value = '07.223.960/0001-60';
  accessKeyField.focus();
  
  if (enabled) {
    accessKeyField.value = key;
    accessKeyField.addEventListener('input', () => {
      if (accessKeyField.value.length >= 44) {
        donateNoteButton.click();
      }
    });
  }
}

async function getCurrentTab() {
  const queryOptions = { active: true, currentWindow: true };
  const [tab] = await chrome.tabs.query(queryOptions);
  return tab;
}
