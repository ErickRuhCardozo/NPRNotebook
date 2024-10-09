/*
 * Author: Erick Ruh Cardozo (W1SD00M) - <erickruhcardozo1998@hotmail.com>
 * Date: Oct 9, 2024 - 9:19 AM 
 */

const tabBarTabs = document.getElementById('tabBarTabs');
const tabBarPages = document.getElementById('tabBarPages');
const closuresTable = document.querySelector('table');
let currentTab = null;
let currentPage = null;
let db = null;
const openDbRequest = indexedDB.open('Closures');

openDbRequest.addEventListener('upgradeneeded', e => {
  const db = e.target.result;
  db.createObjectStore('closures', {keyPath: 'id', autoIncrement: true});
});

openDbRequest.addEventListener('success', e => {
  db = e.target.result
  loadClosures();
});

document.querySelectorAll('button.btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    document.querySelector('.btn-group').classList.add('d-none');
    document.querySelector('.spinner-border').classList.remove('d-none');
    await makeClosure(btn.textContent);
    document.querySelector('.spinner-border').classList.add('d-none');
    document.querySelector('h1').classList.remove('d-none');
  });
});

function setupTabBar() {
  tabBarTabs.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      currentTab?.classList.remove('active');
      currentPage?.classList.add('d-none');
      const tabPage = a.dataset.page;
      const page = tabBarPages.querySelector(`[data-page-${tabPage}]`);
      page.classList.remove('d-none');
      a.classList.add('active');
      currentTab = a;
      currentPage = page;
    });
  });

  currentTab = tabBarTabs.querySelector('a.active');
  currentPage = tabBarPages.querySelector('[data-page-closure]');
}

function loadClosures() {
  const transaction = db.transaction('closures', 'readonly');
  /** @type IDBObjectStore */
  const store = transaction.objectStore('closures');
  store.getAll().addEventListener('success', e => {
    for (const closure of e.target.result) {
      const row = closuresTable.insertRow();
      const totalCell = row.insertCell();
      const dateCell = row.insertCell();
      const collectorCell = row.insertCell();
      const date = new Date(closure.date);
      totalCell.textContent = closure.total.toLocaleString();
      dateCell.textContent = date.toLocaleDateString('pt-BR');
      collectorCell.textContent = closure.collector;
    }
  });
}

async function makeClosure(collector) {
  const data = {total: 0, date: Date.now(), collector: collector};
  const date = new Date();
  const response = await fetch(`https://notaparana.pr.gov.br/nfprweb/app/v1/datatable/documentoFiscalDoado/?mes=${date.getMonth() + 1}&ano=${date.getFullYear()}&draw=1&columns%5B0%5D%5Bdata%5D=cnpjFormatado&columns%5B2%5D%5Bdata%5D=dadosNotaFormatado&start=0&length=1`);

  if (response.status != 200)
    return;

  const json = await response.json();
  data.total = json.recordsTotal;
  const transaction = db.transaction('closures', 'readwrite');
  const store = transaction.objectStore('closures');
  store.add(data);
}

setupTabBar();
