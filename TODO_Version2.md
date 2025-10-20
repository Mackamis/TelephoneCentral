```markdown
# TODO: Telefon‑centrala — plan rada (A — full update)

Datum: 2025-10-20  
Autor: predlog iz ChatGPT / Copilot (ažurirano prema dopunskim informacijama)

Cilj
-----
Implementirati aplikaciju koja simulira telefonsku centralu prema zadatku. Podržati čitanje phones.txt, calls.txt, blocked.txt (calls i blocked mogu se generisati skriptom generate_calls.py). Napraviti preprocesiranje velikih fajlova i omogućiti serijalizaciju učitanih struktura za brzi start.

Sažetak promena (ključne izmene nakon dopunskih informacija)
- Dodata eksplicitna faza preprocesiranja i serijalizacije pre početka rada aplikacije.
- Jasno definisana pravila normalizacije i validacije telefonskih brojeva.
- Definisano ponašanje za blokirane brojeve u live i file-based simulacijama.
- Integracija / korišćenje nonblocking_processes.py u live-call implementaciji.
- Did-you-mean koristi similarity (difflib ili Levenshtein), autocomplete koristi trie + popularnost.
- Trie obavezno za prefiks pretrage (ime, prezime, broj).
- Acceptance kriterijumi i testovi dopunjeni.

Repo struktura (predlog)
- src/
  - main.py                 # CLI / entrypoint
  - data_loader.py          # parsiranje i validacija fajlova; loader za serijalizovano stanje
  - preprocessor.py         # skripta koja pravi serijalizovano stanje iz raw fajlova
  - phonebook.py            # model kontakta, indeksi, insert/remove
  - trie.py                 # tri separate trie-a (firstname, lastname, phoneprefix)
  - calls.py                # model poziva, istorija, file import/export i replay opcija
  - live_call.py            # logika simulacije poziva uživo (timer, prekid) — koristi nonblocking_processes.py
  - popularity_graph.py     # graf popularnosti + update funkcije i scoring
  - blocked.py              # učitavanje i provera blokiranih brojeva
  - search.py               # pretraga (name/surname/number + did-you-mean + autocomplete)
  - simulator.py            # load/stress-test (1 min, 1000 poziva), pause/resume
  - persistence.py          # serijalizacija/deserijalizacija (pickle/JSON) + meta verzija
  - utils.py                # helperi (normalize_number, parsing datuma, formatiranje)
- data/
  - phones.txt
  - calls.txt
  - blocked.txt
  - preprocessed/            # generisano: phonebook.pickle, tries.pickle, popularity.pickle, calls_index.pickle
- tests/
  - test_normalize.py
  - test_blocked_behavior.py
  - test_preprocessor_roundtrip.py
  - test_search_and_autocomplete.py
  - test_popularity_updates.py
- docs/
  - design.md
  - api.md
- TODO.md
- README.md
- generate_calls.py (ako nije već dat)

Milestones (ažurirano)
----------------------

Milestone 0 — Postavka (1 dan)
- [ ] Napraviti repozitorijum i osnovnu strukturu (folderi, README).
- [ ] Mala test data: phones.txt, calls.txt (par desetina redova), blocked.txt.
- [ ] Dodati basic CLI stub (main.py) koji može učitati serijalizovano stanje ili raw fajlove.

Milestone 0.5 — Preprocessing & Serialization (obavezno pre velikih datasetova)
- Zašto: start aplikacije ne sme trajati dugo; veliki fajlovi preprocesirati unapred.
- [ ] Implementirati preprocessor.py: parsiranje phones.txt, calls.txt, blocked.txt -> izgradnja strukturiranog stanja.
  - Generisati i serijalizovati:
    - phonebook dict (number -> Contact)
    - tri trie-a (firstname, lastname, phoneprefix)
    - calls index: number -> List[Call] (sorted po datumu) i globalna lista poziva
    - popularity graph metrika (node metrika + edge info ako želite)
  - Napraviti verzionisani meta fajl (npr. preprocessed/meta.json sa schema_ver)
- [ ] CLI opcija: --rebuild-preprocessed i --load-preprocessed.
- Acceptance: učitavanje serijalizovanog stanja treba trajati sekundе za tipične test fajlove.

Milestone 1 — Osnovni I/O i modeli (2–4 sata)
- [ ] Parsers u data_loader.py s validacijom i sanitizacijom (videti Normalizacija dole).
- [ ] Klase:
  - Contact { number, first_name, last_name, meta }
  - Call { caller, callee, start_datetime, duration_seconds, status } (status: OK | BLOCKED | INVALID)
- [ ] In-memory strukture:
  - Dict number -> Contact
  - List[Call] sortirana po datumu
  - Index: dict number -> List[Call] (append, sort po start na rebuild)
- Tests: parser za invalid/valid redove, logovanje ignorisanih.

Milestone 2 — File-based simulation (zad 2) (2–4 sata)
- [ ] Učitati file (može manji od calls.txt) i za svaki red:
  - Parsirati, normalizovati, validnost.
  - Odrediti status: OK ili BLOCKED (prema trenutnom blocked_set).
  - Ispisati sumarne podatke (caller, callee, start, duration, status). Po defaultu brzo (bez realnog sleep). Opcionalno --replay-rate za real-time replay.
- [ ] Za svaki uspešan (OK) poziv -> update popularity graph.
- Acceptance: svi redovi parsirani/validirani; invalid redovi logovani; blocked pozivi označeni i ne utiču na graf.

Milestone 3 — Istorije poziva (zadaci 3 i 4) (3–6 sati)
- [ ] get_history_between(a,b) -> List[Call] (svi pozivi između datih brojeva, hronološki).
- [ ] get_history_for(number) -> List[Call] (dolazni i odlazni, sa flagom caller/callee).
- [ ] Format ispisa: datum/vreme, dužina, jasno označen pozivalac i pozvani.
- Tests: sortiranje, filteri, edge-cases (prelazak midnight i dur=0).

Milestone 4 — Live-call simulacija (zad 1) (2–4 sata)
- [ ] Implementirati simulate_live_call u live_call.py koristeći nonblocking_processes.py (ako postoji).
- [ ] Pravila:
  - Pre starta: normalizacija brojeva; proveriti blocked_set — ako blocked -> abort i obavesti.
  - Po prekidu: kreirati CallRecord sa statusom OK i duration; append u calls_list; pozvati save callback (append CSV) i popularity_graph.update_on_call.
- [ ] Dve opcije prekida: Enter / "end", ili press-any-key (platform specific) — koristiti nonblocking_processes.py kao primarni mehanizam, fallback na input().
- Acceptance: korisnik prekida without UI freeze; call se beleži samo ako nije blokiran.

Milestone 5 — Pretraga imenika (zad 5) (2–4 sata)
- [ ] Tri nezavisne pretrage (izbor kriterijuma):
  - ime (firstname) — rezultati sortirati po popularnosti (najpre češće pozivani).
  - prezime (lastname) — rezultati mogu biti u proizvoljnom redu (za 10 poena: popularnost).
  - prefiks broja — trie numeric prefix; rezultati mogu biti u proizvoljnom redu ili po popularnosti.
- [ ] Ispis: redni broj rezultata i dostupni podaci (ime, prezime, broj).
- Acceptance: case-insensitive; prefix ignores separators; returns enumerated list.

Milestone 6 — Did-you-mean i Autocomplete (zadaci 7 i 8) (2–4 sata)
- Did-you-mean:
  - [ ] Ako uneseni broj ne postoji, ponuditi top-N sličnih (npr. difflib.get_close_matches ili Levenshtein). Nisu obavezni isti početni prefiksi.
- Autocomplete:
  - [ ] Ponuđeni završeci (do 5) bazirani na trie pretragama i sortirani po popularity score.
- Acceptance: vraća relevantne predloge; autocomplete koristi i trie i popularnost.

Milestone 7 — Popularity graph (zadaci >10 poena) (6–10 sati)
- [ ] Metrički model za popularnost:
  - incoming_count
  - incoming_duration
  - unique_callers_count (ili set)
  - opcionalne težine (npr. duration * 1.0 + calls * 0.5 + unique_callers * 0.3)
- [ ] popularity_graph.update_on_call(call) — ažurira čvorove i ivice.
- [ ] Graf NE briše niti ignoriše blokirane brojeve; blokirani nisu brisani iz grafa.
- [ ] Serijalizovati graf (pickle/JSON) i učitavati pri startu.
- Acceptance: graf se ažurira posle svakog uspešnog poziva (zad 1 & 2 & 9).

Milestone 8 — Trie implementacija i serijalizacija (4–8 sati)
- [ ] Implementirati tri trie-a: firstname, lastname, phoneprefix.
- [ ] API: insert(contact), search_prefix(prefix) -> rezultati.
- [ ] Serijalizovati trie-e (pickle) u preprocessed folder.
- Acceptance: pretrage po prefiksu brže i upotrebljive za autocomplete.

Milestone 9 — Simulacija opterećenja (zad 9) (8–12 sati)
- [ ] simulator.py: generisati 1000 poziva tokom 1 minute (može biti ubrzano u test modu).
  - Proveravati blocked listu pri svakom pozivu.
  - Ažurirati graf popularnosti posle svakog uspešnog poziva.
  - Beležiti najaktivnije korisnike, statistiku trajanja.
  - Omogućiti pause/resume (Event / threading).
- [ ] Po završetku: ispis reporta (Top5 najpopularnijih, prosečno trajanje, broj generisanih poziva, blocked attempts).
- Acceptance: simulator radi deterministički u test modu; graf ažuriran.

Milestone 10 — Testovi, dokumentacija i završetak (2–4 sata)
- [ ] Jedinični testovi za normalizaciju, parsere, graf popularnosti, trie, did-you-mean/autocomplete, blocked behavior, simulator.
- [ ] docs/api.md i primeri pokretanja.
- [ ] Profilisanje i optimizacija po potrebi.

Normalizacija i validacija telefonskih brojeva (obavezno)
- Pravila:
  - Ukloniti dozvoljene separatore: razmak, '-', '(', ')', '+'.
  - Nakon čišćenja mora ostati samo cifre; u suprotnom : broj NEVAŽEĆI.
  - Prazan ili ne‑numerički nakon čišćenja -> smatrati invalid i ignorisati taj poziv (ili označiti status=INVALID prilikom file-based uvoza).
- Tests: test_normalize.py pokriva razne varijante.

Ponašanje sa blokiranim brojevima (precizno)
- Live call (zad 1):
  - Pre starta poziva -> ako caller ili callee u blocked_set => abort i obavesti korisnika.
  - Takav poziv se ne beleži kao uspešan poziv i ne utiče na graf.
- File-based simulation (zad 2):
  - Pri importu, sve zapise čuvati, ali pri simulaciji svakog poziva:
    - Ako caller ili callee trenutno blokiran -> označiti poziv kao BLOCKED (status) i ne ažurirati graf.
    - Sumarni ispis treba naglasiti status svakog poziva (OK/BLOCKED/INVALID).
- Graf popularnosti:
  - Ne briše se čvor ako je broj blokiran; istorija ostaje.

Did-you-mean i Autocomplete (implementacione napomene)
- Did-you-mean:
  - Koristiti difflib.get_close_matches (standard) ili python-Levenshtein ako želiš precizniju kontrolu.
  - Candidate pool: svi brojevi (bez/sa formattingom) + ime/prezime kombinacije.
- Autocomplete:
  - Koristiti trie za skup potencijalnih završetaka, sortirati predloge po popularity score iz grafa.
  - Case-insensitive; vratiti do 5 posebno rangiranih predloga.

Format fajlova (preporučeno)
- phones.txt: CSV: number,first_name,last_name,meta...
- calls.txt: CSV: caller,callee,start_iso8601,duration_seconds
- blocked.txt: jedan broj po redu ili CSV number,reason
- preprocessed/: phonebook.pickle, tries.pickle, popularity.pickle, calls_index.pickle, meta.json

Serijalizacija (preproces + runtime save/load)
- Predlog: pickle za strukture (trie, graph, indices) + JSON za metrike/metadata.
- Verzija: svaki serijalizovani paket treba meta.json sa schema_version i created_at.
- CLI: --save-state, --load-state.

API/Signatures preporučeni
- data_loader.load_phones(path) -> Dict[number, Contact]
- data_loader.load_calls(path, validate=True) -> List[Call]
- preprocessor.build_and_save(raw_paths, out_dir)
- persistence.save_state(out_dir, state_objects)
- persistence.load_state(state_dir) -> state_objects
- phonebook.insert(contact)
- trie.insert(key, contact_ref)
- search.find_by_name(name) -> List[Contact] (sorted by popularity)
- search.find_by_number_prefix(prefix) -> List[Contact]
- calls.get_history_between(a,b) -> List[Call]
- calls.get_history_for(n) -> List[Call]
- popularity.update_on_call(call)
- simulator.run(duration_seconds=60, total_calls=1000, pause_event=Event())

Logging i error reporting
- Pri parsiranju velikih fajlova: napraviti summary (valid/invalid/blocked counts) i log fajl data/preprocessor.log.
- Pri ignorisanju redova (invalid broj/format), logovati liniju i razlog (invalid format / letters / empty).

Test plan (obavezno)
- test_normalize.py: razni layouti brojeva.
- test_blocked_behavior.py: live abort i file mark blocked.
- test_preprocessor_roundtrip.py: build -> save -> load -> compare structures.
- test_search_and_autocomplete.py: trie + popularity ordering.
- test_popularity_updates.py: update nakon pojedinačnih poziva i bulk.

Acceptance kriterijumi (kratko)
- Start using preprocessed state < ~3s (test dataset).
- Live poziv: prekid bez zamrzavanja UI; poziv ne ide ako je strana blokirana; successful call ažurira graph.
- File-based sim: invalid redovi logovani; blocked pozivi označeni; successful pozivi ažuriraju graph.
- Did-you-mean: vraća top 3 slična broja/imenа.
- Autocomplete: vraća do 5 predloga sortirano po popularity score.
- Simulator: generiše 1000 poziva u simuliranom 1-min intervalu (test mode ubrzan) i daje izveštaj top5 i avg duration.

Kratki primer CLI komandi (predlog)
- python -m src.main --load-state data/preprocessed
- python -m src.main --rebuild-preprocessed --phones data/phones.txt --calls data/calls.txt --blocked data/blocked.txt
- python -m src.main live-call
- python -m src.main file-sim --file tests/sample_calls.csv --replay-rate fast
- python -m src.main search --name "Marko"
- python -m src.main simulator --calls 1000 --duration 60

Dodatne napomene za implementaciju
- Koristiti thread-safe strukture pri paralelnim upisima (simulator).
- Pri append-u u calls.txt koristiti file-locking ili queue writer thread.
- Ako dataset postane veliki razmotriti sqlite (lakše query i manja memorija).
- Nonblocking input: preferirati funkcije iz nonblocking_processes.py; fallback input().

Checklist (kratki task set za početak)
- [ ] Implementirati normalize_number funkciju i testove.
- [ ] Implementirati data_loader parsere i logovanje invalid redova.
- [ ] Implementirati preprocessor.py sa serijalizacijom.
- [ ] Implementirati basic popularity_graph stub i test update.
- [ ] Implementirati live_call koji koristi nonblocking_processes.py.
- [ ] Implementirati trie i integrisati u search/autocomplete.
- [ ] Implementirati simulator (stress mode).
- [ ] Napisati jedinične testove i dokumentaciju.

```