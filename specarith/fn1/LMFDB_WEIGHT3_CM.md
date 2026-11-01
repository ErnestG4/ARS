# LMFDB lookup: weight-3 CM newforms of level |D|, D in {-7,-8,-11,-19,-43,-67,-163}

Read-only lookup, 2026-10-31. No coefficients computed locally; everything below is as read off LMFDB pages.

## How the pages were read (access notes, stated honestly)

- Plain `curl` to www.lmfdb.org returns a reCAPTCHA "Checking your browser" page for every URL (search, newform,
  API). Nothing was read that way.
- Two fetchers did get through:
  - **Exa web_fetch**: returns the page's raw text verbatim. Used for the level 8/11/19/43/67/163 search pages and the
  7.3.b.a, 8.3.d.a, 11.3.b.a, 4.5.b.a and 3.7.b.a newform pages. It returned SOURCE_NOT_AVAILABLE for the
  19/43/67/163 newform pages and for every L-function page it was tried on: 163.3.b.a, 4.5.b.a and 3.7.b.a, plus
  their label-style URLs.
  - **WebFetch**: the page goes through a small extraction model, so the output is a transcription. Used for the
  19/43/67/163 newform pages, the level-7 search page and the L-function pages. LMFDB intermittently served it the
  reCAPTCHA page as well.
- Grades: **VERIFIED** means read on the page. "(Exa, verbatim)" or "(WebFetch, transcribed)" says which route was used.
  For every WebFetch-transcribed a_p list, two independent tables on the same page were cross-checked: the q-expansion
  and the "Hecke characteristic polynomials" table (dimension 1, so F_p(T) = T - a_p). They agree at every prime
  <= 50 listed below.
- **NOT FOUND** means the page could not be loaded (reCAPTCHA every time) or the item is not on the page.

### L-function functional-equation convention on LMFDB pages
Each L-function page has a "Normalization: arithmetic | analytic" toggle and shows two functional-equation lines
under "Functional equation". The line with Γ_C(s) and Λ(3−s) (centre s = 3/2) is the arithmetic one. The line with
Γ_C(s+1) and Λ(1−s) (centre s = 1/2) is the analytic one. The pages for 7, 8 and 19 were transcribed with those
headings attached. For 11 and 67 the extraction said the lines sit under one "Functional equation" heading with the
toggle, so the pairing is by centre and not by a printed label. The lines below are the page LaTeX with `\mathstrut`
and `&`/`\cr` alignment removed.

## Search results by level (weight 3)

Each search page says "The results below are complete, since the LMFDB contains all newforms with Nk^2 at most 4000".

| Level | URL | Forms with CM | Other forms (no CM) | Route |
|---|---|---|---|---|
| 7 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=7&weight=3 | 7.3.b.a (CM Q(√−7)) | none ("unique" result) | WebFetch |
| 8 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=8&weight=3 | 8.3.d.a (CM Q(√−2)) | none ("unique match") | Exa |
| 11 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=11&weight=3 | 11.3.b.a (CM Q(√−11)) | 11.3.d.a (dim 4) | Exa |
| 19 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=19&weight=3 | 19.3.b.a (CM Q(√−19)) | 19.3.b.b (dim 2), 19.3.d.a (6), 19.3.f.a (12) | Exa |
| 43 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=43&weight=3 | 43.3.b.a (CM Q(√−43)) | 43.3.b.b (6), 43.3.d.a (12), 43.3.f.a (42), 43.3.h.a (72) | Exa |
| 67 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=67&weight=3 | 67.3.b.a (CM Q(√−67)) | 67.3.b.b (10), 67.3.d.a (20), 67.3.f.a (110), 67.3.h.a (200) | Exa |
| 163 | https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?level=163&weight=3 | 163.3.b.a (CM Q(√−163)) | 163.3.b.b (26), 163.3.d.a (54), 163.3.f.a (162), 163.3.h.a (486), 163.3.j.a (1404) | Exa |

At each level, exactly one weight-3 newform orbit has CM, and it is listed with dimension 1 and coefficient field Q.

## Per-field results

### D = −7: 7.3.b.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/7/3/b/a/ (Exa, verbatim).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/7/3/b/a/ (WebFetch).

1. VERIFIED. Label 7.3.b.a. Character orbit 7.b ("of order 2, degree 1, minimal"; gp `Mod(6,7)`, i.e. Conrey 7.6).
   Dimension 1. Self dual yes. Analytic conductor 0.190736185052. Analytic rank 0. Coefficient field Q, ring Z.
   CM discriminant −7. Inner twists: "7.b | odd | 2 | 1 | CM by Q(√−7)". Sato–Tate group U(1)[D_2].
   The page also says "This is the first CM form with weight at least 2, when ordered by analytic conductor" and gives
   the eta quotient f(z) = η(z)^3 η(7z)^3.
2. VERIFIED. L-function label 2-7-7.6-c2-0-0.
   - Arithmetic: Λ(s) = 7^{s/2} Γ_C(s) L(s) = Λ(3−s)
   - Analytic: Λ(s) = 7^{s/2} Γ_C(s+1) L(s) = Λ(1−s)
   - Degree 2. Conductor 7. Sign 1. Analytic conductor 0.190736. Root analytic conductor 0.436733. Motivic weight 2.
   Primitive yes. Self-dual yes. Analytic rank 0.
   - Selberg data (2, 7, ( :1), 1).
3. VERIFIED (q-expansion and char-poly table agree). a_p for p ≤ 50:
   a2=−3, a3=0, a5=0, a7=−7, a11=−6, a13=0, a17=0, a19=0, a23=18, a29=−54, a31=0, a37=−38, a41=0, a43=58, a47=0.
4. NOT FOUND. The newform page names no Hecke/Grössen character. The L-function "Origins" list has only
   "Modular form 7.3.b.a" and "Modular form 7.3.b.a.6.1".

### D = −8: 8.3.d.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/8/3/d/a/ (Exa, verbatim).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/8/3/d/a/ (WebFetch).

1. VERIFIED. Label 8.3.d.a. Character orbit 8.d ("of order 2, degree 1, minimal"; gp `Mod(3,8)`, Conrey 8.3;
   χ(5) = −1, χ(7) = −1). Dimension 1. Self dual yes. Analytic conductor 0.217984211488. Analytic rank 0.
   Coefficient field Q. CM discriminant −8. Inner twists: "8.d | odd | 2 | 1 | CM by Q(√−2)".
   Sato–Tate group U(1)[D_2]. Eta quotient η(z)^2 η(2z) η(4z) η(8z)^2.
2. VERIFIED. L-function label 2-2e3-8.3-c2-0-0.
   - Arithmetic: Λ(s) = 8^{s/2} Γ_C(s) L(s) = Λ(3−s)
   - Analytic: Λ(s) = 8^{s/2} Γ_C(s+1) L(s) = Λ(1−s)
   - Degree 2. Conductor 8 = 2^3. Sign 1. Analytic conductor 0.217984. Root analytic conductor 0.466887.
   Motivic weight 2. Primitive yes. Self-dual yes. Analytic rank 0.
   - Selberg data (2, 8, ( :1), 1).
3. VERIFIED (q-expansion and char-poly table agree). a_p for p ≤ 50:
   a2=−2, a3=−2, a5=0, a7=0, a11=14, a13=0, a17=2, a19=−34, a23=0, a29=0, a31=0, a37=0, a41=−46, a43=14, a47=0.
4. NOT FOUND. The L-function "Origins" list has only "Modular form 8.3.d.a" and "Modular form 8.3.d.a.3.1". The
   extraction reported "The page lists no Hecke character".

### D = −11: 11.3.b.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/11/3/b/a/ (Exa, verbatim).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/11/3/b/a/ (WebFetch).

1. VERIFIED. Label 11.3.b.a. Character orbit 11.b (order 2, minimal; gp `Mod(10,11)`, Conrey 11.10).
   Dimension 1. Self dual yes. Analytic conductor 0.299728290796. Analytic rank 0. Coefficient field Q.
   CM discriminant −11. Inner twists: "11.b | odd | 2 | 1 | CM by Q(√−11)". Sato–Tate group U(1)[D_2].
2. VERIFIED. L-function label 2-11-11.10-c2-0-0.
   - Λ(s) = 11^{s/2} Γ_C(s) L(s) = Λ(3−s) (arithmetic, centre 3/2)
   - Λ(s) = 11^{s/2} Γ_C(s+1) L(s) = Λ(1−s) (analytic, centre 1/2)
   - Both lines sit under the "Functional equation" heading with the normalisation toggle.
   - Degree 2. Conductor 11. Sign 1. Analytic conductor 0.299728. Root analytic conductor 0.547474.
   Motivic weight 2. Primitive yes. Self-dual yes. Analytic rank 0.
   - Selberg data (2, 11, ( :1), 1).
3. VERIFIED (q-expansion and char-poly table agree). a_p for p ≤ 50:
   a2=0, a3=−5, a5=−1, a7=0, a11=−11, a13=0, a17=0, a19=0, a23=35, a29=0, a31=−37, a37=−25, a41=0, a43=0, a47=50.
4. NOT FOUND. The L-function Origins list has only "Modular form 11.3.b.a" and "Modular form 11.3.b.a.10.1".

### D = −19: 19.3.b.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/19/3/b/a/ (WebFetch, transcribed; Exa
SOURCE_NOT_AVAILABLE).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/19/3/b/a/ (WebFetch).

1. VERIFIED. Label 19.3.b.a. Character orbit 19.b. Dimension 1. Self dual yes. Analytic conductor 0.517712502285.
   Analytic rank 0. Coefficient field Q (ring Z, index 1). CM discriminant −19. Inner twists 2:
   "19.b | odd | 2 | 1 | CM by Q(√−19)".
2. VERIFIED. L-function label 2-19-19.18-c2-0-1.
   - Arithmetic: Λ(s) = 19^{s/2} Γ_C(s) L(s) = Λ(3−s)
   - Analytic: Λ(s) = 19^{s/2} Γ_C(s+1) L(s) = Λ(1−s)
   - Degree 2. Conductor 19. Sign 1. Analytic conductor 0.517712. Root analytic conductor 0.719522.
   Motivic weight 2. Primitive yes. Self-dual yes. Analytic rank 0.
   - Selberg data (2, 19, ( :1), 1).
3. VERIFIED (WebFetch; q-expansion through q^47 and char-poly table agree). a_p for p ≤ 50:
   a2=0, a3=0, a5=−9, a7=−5, a11=3, a13=0, a17=15, a19=−19, a23=−30, a29=0, a31=0, a37=0, a41=0, a43=−85, a47=75.
4. NOT FOUND. The extraction reports that the page never uses "Hecke character" or "Grossencharacter". The
   L-function Origins list has only "Modular form 19.3.b.a" and "Modular form 19.3.b.a.18.1".

### D = −43: 43.3.b.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/43/3/b/a/ (WebFetch, transcribed; Exa
SOURCE_NOT_AVAILABLE).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/43/3/b/a (WebFetch; the URL with a trailing slash
got the reCAPTCHA page first).

1. VERIFIED. Label 43.3.b.a. Character orbit 43.b. Dimension 1. Self dual yes. Analytic conductor 1.17166513675.
   Analytic rank 0. Coefficient field Q (ring Z, index 1). CM discriminant −43. Inner twists 2:
   "43.b | odd | 2 | 1 | CM by Q(√−43)".
2. VERIFIED. L-function label 2-43-43.42-c2-0-3.
   - Λ(s) = 43^{s/2} Γ_C(s) L(s) = Λ(3−s) (arithmetic, centre 3/2)
   - Λ(s) = 43^{s/2} Γ_C(s+1) L(s) = Λ(1−s) (analytic, centre 1/2)
   - Degree 2. Conductor 43. Sign 1. Analytic conductor 1.17166. Root analytic conductor 1.08243.
   Motivic weight 2. Primitive yes. Self-dual yes. Analytic rank 0.
   - Selberg data (2, 43, ( :1), 1).
3. VERIFIED (WebFetch; q-expansion through q^99 and char-poly table agree). a_p for p ≤ 50:
   a2=0, a3=0, a5=0, a7=0, a11=−21, a13=−17, a17=−9, a19=0, a23=3, a29=0, a31=19, a37=0, a41=39, a43=−43, a47=−78.
4. NOT FOUND. The L-function Origins list has only "Modular form 43.3.b.a" and "Modular form 43.3.b.a.42.1".

### D = −67: 67.3.b.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/67/3/b/a/ (WebFetch, transcribed; Exa
SOURCE_NOT_AVAILABLE).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/67/3/b/a/ (WebFetch).

1. VERIFIED. Label 67.3.b.a. Character orbit 67.b. Dimension 1. Self dual yes. Analytic conductor 1.826.
   Analytic rank 0. Coefficient field Q (ring Z, index 1). CM discriminant −67. Inner twists 2:
   "67.b | odd | 2 | 1 | CM by Q(√−67)".
2. VERIFIED. L-function label 2-67-67.66-c2-0-5.
   - Λ(s) = 67^{s/2} Γ_C(s) L(s) = Λ(3−s) (arithmetic, centre 3/2)
   - Λ(s) = 67^{s/2} Γ_C(s+1) L(s) = Λ(1−s) (analytic, centre 1/2)
   - Degree 2. Conductor 67. Sign 1. Analytic conductor 1.82561. Root analytic conductor 1.35115.
   Motivic weight 2. Primitive yes. Self-dual yes. Analytic rank 0.
   - Selberg data (2, 67, ( :1), 1).
3. VERIFIED (WebFetch; q-expansion and char-poly table agree). a_p for p ≤ 50:
   a2=0, a3=0, a5=0, a7=0, a11=0, a13=0, a17=−33, a19=−29, a23=−21, a29=−9, a31=0, a37=7, a41=0, a43=0, a47=27.
4. NOT FOUND. The L-function Origins list has only "Modular form 67.3.b.a" and "Modular form 67.3.b.a.66.1".

### D = −163: 163.3.b.a
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/163/3/b/a/ (WebFetch, transcribed; Exa
SOURCE_NOT_AVAILABLE).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/163/3/b/a/ (reCAPTCHA on every attempt).

1. VERIFIED. Label 163.3.b.a. Character orbit 163.b. Dimension 1. Self dual yes. Analytic conductor 4.441.
   Analytic rank 0. Coefficient field Q (ring Z, index 1). CM discriminant −163. Inner twists 2:
   "163.b | odd | 2 | 1 | CM by Q(√−163)".
2. NOT FOUND. Every fetch of the L-function page, with and without the trailing slash, returned the LMFDB reCAPTCHA
   page. The search page gives the analytic conductor 4.441, which is a newform property and not read from the
   L-function page.
3. VERIFIED (WebFetch; q-expansion through q^99 and char-poly table agree). a_p for p ≤ 50:
   a2=a3=a5=a7=a11=a13=a17=a19=a23=a29=a31=a37=0, a41=−81, a43=−77, a47=−69.
   The page shows these as F_p(T) = T for every p ≤ 37, then F_41 = T+81, F_43 = T+77 and F_47 = T+69.
4. NOT FOUND. The newform page has no Hecke-character statement, and the L-function page could not be loaded.

## Comparison forms

### 4.5.b.a (CM by Q(i))
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/4/5/b/a/ (Exa, verbatim).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/4/5/b/a/ and the label URL
https://www.lmfdb.org/L/2/2e2/4.3/c4/0/0 both returned reCAPTCHA (WebFetch) or SOURCE_NOT_AVAILABLE (Exa).

1. VERIFIED. Label 4.5.b.a. Level 4. Weight 5. Character orbit 4.b ("of order 2, degree 1, minimal"; gp `Mod(3,4)`,
   Conrey 4.3). Dimension 1. Self dual yes. Analytic conductor 0.413479852335. Analytic rank 0. Coefficient field Q.
   CM discriminant −4. Inner twists: "4.b | odd | 2 | 1 | CM by Q(√−1)". Sato–Tate group U(1)[D_2].
   Eta quotient η(z)^4 η(2z)^2 η(4z)^4.
2. NOT FOUND. The L-function page could not be loaded.
3. VERIFIED (Exa, verbatim plain-text q-expansion through q^98). a_p for p ≤ 50:
   a2=−4, a3=0, a5=−14, a7=0, a11=0, a13=−238, a17=322, a19=0, a23=0, a29=82, a31=0, a37=2162, a41=−3038, a43=0,
   a47=0.

### 3.7.b.a (CM by Q(√−3))
Newform: https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/3/7/b/a/ (Exa, verbatim).
L-function: https://www.lmfdb.org/L/ModularForm/GL2/Q/holomorphic/3/7/b/a/ and the label URL
https://www.lmfdb.org/L/2/3/3.2/c6/0/0 both returned reCAPTCHA (WebFetch) or SOURCE_NOT_AVAILABLE (Exa).

1. VERIFIED. Label 3.7.b.a. Level 3. Weight 7. Character orbit 3.b ("of order 2, degree 1, minimal"; gp `Mod(2,3)`,
   Conrey 3.2). Dimension 1. Self dual yes. Analytic conductor 0.690162250860. Analytic rank 0. Coefficient field Q.
   CM discriminant −3. Inner twists: "3.b | odd | 2 | 1 | CM by Q(√−3)". Sato–Tate group U(1)[D_2].
2. NOT FOUND. The L-function page could not be loaded.
3. VERIFIED (Exa, verbatim plain-text q-expansion through q^97). a_p for p ≤ 50:
   a2=0, a3=−27, a5=0, a7=−286, a11=0, a13=506, a17=0, a19=−10582, a23=0, a29=0, a31=35282, a37=−89206, a41=0,
   a43=111386, a47=0.

## Summary table (a_p, p ≤ 50, as read)

| p | 7.3.b.a | 8.3.d.a | 11.3.b.a | 19.3.b.a | 43.3.b.a | 67.3.b.a | 163.3.b.a | 4.5.b.a | 3.7.b.a |
|---|---|---|---|---|---|---|---|---|---|
| 2 | −3 | −2 | 0 | 0 | 0 | 0 | 0 | −4 | 0 |
| 3 | 0 | −2 | −5 | 0 | 0 | 0 | 0 | 0 | −27 |
| 5 | 0 | 0 | −1 | −9 | 0 | 0 | 0 | −14 | 0 |
| 7 | −7 | 0 | 0 | −5 | 0 | 0 | 0 | 0 | −286 |
| 11 | −6 | 14 | −11 | 3 | −21 | 0 | 0 | 0 | 0 |
| 13 | 0 | 0 | 0 | 0 | −17 | 0 | 0 | −238 | 506 |
| 17 | 0 | 2 | 0 | 15 | −9 | −33 | 0 | 322 | 0 |
| 19 | 0 | −34 | 0 | −19 | 0 | −29 | 0 | 0 | −10582 |
| 23 | 18 | 0 | 35 | −30 | 3 | −21 | 0 | 0 | 0 |
| 29 | −54 | 0 | 0 | 0 | 0 | −9 | 0 | 82 | 0 |
| 31 | 0 | 0 | −37 | 0 | 19 | 0 | 0 | 0 | 35282 |
| 37 | −38 | 0 | −25 | 0 | 0 | 7 | 0 | 2162 | −89206 |
| 41 | 0 | −46 | 0 | 0 | 39 | 0 | −81 | −3038 | 0 |
| 43 | 58 | 14 | 0 | −85 | −43 | 0 | −77 | 0 | 111386 |
| 47 | 0 | 0 | 50 | 75 | −78 | 27 | −69 | 0 | 0 |

Every L-function page that loaded (7, 8, 11, 19, 43, 67) gives sign 1, motivic weight 2, Selberg data
(2, N, ( :1), 1) and conductor N equal to the level.
