# cermati.com — recon for the SEIT take-home (Skenario 1 & 2)

Point-in-time recon of www.cermati.com (desktop viewport 1440x900, Oct 2026 era markup). Re-verify before relying on any value here; routes and markup change without notice.

## Skenario 1 — compare Syariah Pasar Uang products

| Step | Reality |
|---|---|
| Homepage | `https://www.cermati.com/` |
| "Investasi" | NOT a navbar item. It is an accordion header inside the "Layanan Keuangan" card: the clickable row carries `id="investments"`. Clicking it expands two cards. |
| Cards | `#digitalGold` (Emas Digital) and `#mutualFund` (Reksa Dana), each with a `button` whose text is `Buka`. Scope to `#mutualFund button`; do not index the page-wide "Buka" list. |
| Expanding | The collapsed content sits in a `max-height: 0` wrapper, so children still report `isDisplayed() === true`. Use `isClickable()` on the Buka button as the state check. |
| Reksa Dana landing | `/reksadana` — `h1` = "Solusi Investasi Reksa Dana Mudah dan Tepercaya" |
| Pasar Uang | `a[href="/reksadana/pasar-uang"]` inside "Pilihan Investasi Reksa Dana" |
| Pasar Uang list | `/reksadana/pasar-uang`, ~25 cards |

Product list page details:

- Card attribute: `div.product-item-card[data-item="<product name>"]` (also `data-button-name="click_mutualfund_product_detail_listingpage"`).
- Inside a card: `.product-name`, `.product-name-container .text-support` (fund type; plain `.text-support` matches 5 nodes per card), `.product-return span`, `.product-expense-ratio span`, `.product-aum span`.
- Bottom control bar: `div.react-bottom-control-panel` holding three buttons labelled `Urutkan`, `Filter`, `Bandingkan`.

Filter flow (three actions, not one):

1. Click the `Filter` button in `.react-bottom-control-panel`.
2. A drawer appears (`div.react-product-list-filter__item` blocks). Option groups are `div.form-group`; the Syariah option is `label.checkbox-kit > input[name="isShariaFilterActive"]` with a `span.control-label` drawing the box. Click the label.
3. Click `Terapkan` inside the drawer. Until then the list does not change and no URL param appears.

After applying: URL gains `?is-sharia-filter-active=true` and the list drops to the Syariah funds (8 at the time of writing, every name containing "Syariah"). The cards carry no Syariah badge, so the query string plus fund-name wording are the only proofs; a conventional fund such as `Henan Ultima Money Market` disappears.

Compare flow:

1. Click `Bandingkan` in the bottom bar. This opens `div.comparison-bottom-sheet > div.comparison-card` with three slots `p.content__product-box` ("Pilihan 1..3") and reveals a `.product-checkbox` per card: `label.checkbox-kit.no-label > input[type=checkbox]` + `span.control-label`.
2. The checkbox is covered by the card header div, so pointer and label clicks do nothing. `input.click()` dispatched through `browser.execute` is what fires React's change handler and fills a slot with the fund name.
3. With two slots filled, `button.btn-action.btn-full` inside `.comparison-card` enables. Clicking it navigates to `/reksadana/bandingkan?fund1=<slug>&fund2=<slug>&fund3=`.

Comparison page selectors:

- Fund names: `.compared-product-section > div > p.text-support` (the trailing "Pilih Reksa Dana" sits in a `button`, so it is excluded).
- Metric rows: `.compared-metric-section > div`, label in `.no-margin`, values in `.sub-section-container__box` (the third slot box is empty and must be filtered out).
- Rows include `Return 1 Tahun`, `CAGR 1 Tahun`, `Max. Drawdown 1 Tahun`, `Expense Ratio`, `Total AUM`, `Jenis Produk`, `Level Risiko`, `Min. Pembelian`.
- The section renders before its data arrives, so wait until the name count equals the number compared.

## Skenario 2 — search "BCA"

- Search trigger: `button[aria-label="Buka Pencarian"]` in the header (top-left on desktop).
- Input: `input[name="term"]`, placeholder `Cari di Cermati.com`, inside `form.SearchBox_search-box__<hash>` (hash → do not depend on it). Enter submits.
- Results URL: **`/cari?term=BCA`**. `/search?term=BCA` returns the 404 page — a wrong guess here looks like "search is broken".
- Total line: a `div` whose text starts with `Ditemukan`, containing a direct `<strong>`: `Ditemukan <strong>57</strong> hasil dari pencarian <strong>"<em>BCA</em>"</strong>`. The direct-child `strong` distinguishes it from every wrapper above it.
- Category counts: `a[href*="tag="]` that contains `span.badge`, e.g. `Kartu Kredit<span class="badge pull-right">0</span>`. Tags are `creditCard|loan|saving|article|promotion`.
- **`Semua` has no badge** — filter on badge presence and it excludes itself. Observed: 0 + 7 + 0 + 25 + 25 = 57, matching `Ditemukan 57 hasil`. The brief's example (58) is illustrative only.

## General site quirks

- Next.js client rendering; content is absent until hydration, so query after a `waitForDisplayed`/`waitUntil` on a known element.
- At ~800px wide the header loses `Investasi`/`Produk` and switches to a mobile bottom-nav (`Beranda`, `Produk`, `Akun`) — always set a desktop window size.
- Classes are a mix of stable domain names (`product-item-card`, `checkbox-kit`, `compared-metric-section`) and hashed CSS modules (`Header_header__gtmFw`, `btn_SSfdi`, `Collapsible_collapsible__17RaW`). Use the former, never the latter.
- The site is reachable from a headless Chromium session with no anti-bot challenge, but keeping one session per feature file avoids looking like a crawler.
