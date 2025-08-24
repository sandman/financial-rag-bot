const params = new URLSearchParams(location.search);
const name = params.get('name');
const page = parseInt(params.get('page') || '0', 10) || 0;
const text = params.get('text') || '';
const src = `/pdf/${encodeURIComponent(name)}`;

const CMAP_URL = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/cmaps/';
const pdfjsLib = window['pdfjsLib'];
const pdfjsViewer = window['pdfjsViewer'];
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';

const container = document.getElementById('viewerContainer');
const viewer = document.getElementById('viewer');
const eventBus = new pdfjsViewer.EventBus();
const pdfLinkService = new pdfjsViewer.PDFLinkService({ eventBus });
const pdfFindController = new pdfjsViewer.PDFFindController({ eventBus, linkService: pdfLinkService });
const pdfViewer = new pdfjsViewer.PDFViewer({
  container,
  viewer,
  eventBus,
  linkService: pdfLinkService,
  findController: pdfFindController,
  textLayerMode: 2, // enable text layer for highlighting
});
pdfLinkService.setViewer(pdfViewer);

async function open() {
  const loadingTask = pdfjsLib.getDocument({ url: src, cMapUrl: CMAP_URL, cMapPacked: true });
  const pdfDocument = await loadingTask.promise;
  pdfViewer.setDocument(pdfDocument);
  pdfLinkService.setDocument(pdfDocument, null);
  eventBus.on('pagesinit', () => {
    if (page > 0 && page <= pdfDocument.numPages) {
      pdfViewer.currentPageNumber = page;
    }
  });

  // Custom textLayer highlighter fallback (handles whitespace/segment mismatches)
  let didHighlight = false;
  eventBus.on('textlayerrendered', (evt) => {
    if (didHighlight) return;
    if (page && evt.pageNumber !== page) return;
    const query = decodeURIComponent(text || '').trim();
    if (!query) return;
    const words = query.toLowerCase().split(/\s+/).filter(Boolean);
    const pageNode = viewer.querySelector(`.page[data-page-number='${page}'] .textLayer`);
    if (!pageNode) return;
    const spans = pageNode.querySelectorAll('span');
    let firstHit = null;
    spans.forEach((sp) => {
      const s = (sp.textContent || '').toLowerCase();
      if (words.some((w) => w.length > 2 && s.includes(w))) {
        sp.classList.add('custom-highlight');
        if (!firstHit) firstHit = sp;
      }
    });
    if (firstHit) {
      firstHit.scrollIntoView({ block: 'center' });
      didHighlight = true;
    }
  });
}

open();


