# Tinklo srauto valdiklis „Umbrel OS 2.0“

Parengta 2026-10-13. Tai asmeninis, neoficialus programos paketas, o ne „Umbrel“ sistemos modifikacija. Paketas paruoštas diegimui per asmeninę Community App Store saugyklą. Jis dar nebuvo paleistas tikrame „Umbrel“ įrenginyje: atlikti vietiniai skaičiavimo testai nepakeičia pirmojo diegimo patikros.

## Kas patikrinta

Oficialus stabilus kodas: `getumbrel/umbrel`, žyma `2.0.0`, commit `9298257b0e904ca8d8270b1702672666343f0b86`.

- Sistemos valdikliai turi saugyklos, atminties ir CPU rodmenis; integruoto RX/TX valdiklio šiame registre nėra.
- Programų `widgets` palaikomi; `three-stats` leidžia rodyti Download RX, Upload TX ir sąsają.
- `endpoint` turi nurodyti Compose paslaugą (`web:8080/widget`). „Umbrel“ pats pakeičia paslaugos vardą į konteinerio IP.
- JSON atsakyme būtini `type`, `refresh` ir pasirinkto tipo duomenys. Čia naudojamas `refresh: "2s"`.
- 2.0.0 leidžia iki trijų įjungtų valdiklių vienai paskyrai. Jei vietos nėra, išjunkite vieną esamą.

Šaltiniai:

- [2.0.0 sistemos valdikliai](https://github.com/getumbrel/umbrel/blob/2.0.0/packages/umbreld/source/modules/system/system-widgets.ts)
- [2.0.0 valdiklių API ir limitas](https://github.com/getumbrel/umbrel/blob/2.0.0/packages/umbreld/source/modules/widgets/routes.ts)
- [2.0.0 programos valdiklio duomenų gavimas](https://github.com/getumbrel/umbrel/blob/2.0.0/packages/umbreld/source/modules/apps/app.ts#L2805)
- [Oficiali programų pakavimo dokumentacija, Widgets](https://github.com/getumbrel/umbrel-apps/blob/master/.agents/skills/umbrel-package-app/SKILL.md#widgets)
- [Oficialus Community App Store šablonas](https://github.com/getumbrel/umbrel-community-app-store)

## Įdiegimas be sistemos failų taisymo

1. Išskleiskite ZIP. Sukurkite savo GitHub saugyklą, pvz., `umbrel-network-widget`. Naudokite viešą saugyklą, kurioje nėra slaptažodžių ar asmeninių duomenų.
2. Į saugyklos ŠAKNĮ įkelkite `umbrel-app-store.yml` ir visą `netmeter-traffic` aplanką. Nekelkite juos į papildomą `umbrel-network-widget` poaplankį. `src` ir `data/state/.gitkeep` turi išlikti. Pridėkite ir šį README. GitHub įkėlimo lange patikrinkite, ar išliko paslėptas `.gitkeep` failas; prireikus sukurkite jį per „Add file“.
3. Programos naršyklės prievadas yra **38921**. Jei jį naudoja kita jūsų programa, prieš diegimą pakeiskite `port` reikšmę `netmeter-traffic/umbrel-app.yml` į laisvą prievadą, ne iš 40000–49999 intervalo. Vidinio `APP_PORT: 8080` nekeiskite.
4. „Umbrel“ App Store atverkite bendruomenės / pasirinktinės parduotuvės pridėjimo veiksmą ir įklijuokite savo GitHub saugyklos adresą. Tai turi būti saugyklos URL, ne ZIP failo nuoroda. Konkretaus meniu pavadinimas priklauso nuo sąsajos kalbos.
5. Parduotuvėje „Personal Network Widgets“ įdiekite „Network Traffic“.
6. Atverkite įdiegtą programą. Po kelių sekundžių turi atsirasti Download ir Upload skaičiai bei sąsajos pavadinimas.
7. Darbalaukio valdiklių pasirinkime pridėkite „Network Traffic“. Jei jau įjungti trys valdikliai, pirmiau pašalinkite vieną iš darbalaukio.

Saugyklos paskelbimas ir diegimas nėra atlikti automatiškai. Paketui nereikia rankiniu būdu paleisti `docker compose`, SSH, `sudo`, išjungti „Umbrel“ prisijungimo ar keisti OS failų.

## Tinkamos sąsajos pasirinkimas

Numatytasis `NET_INTERFACE=auto` parenka mažiausios metrikos IPv4 numatytojo maršruto sąsają. Pavadinimas matomas programoje ir valdiklyje. Programa taip pat rodo galimų sąsajų sąrašą.

VPN, kelių tinklo jungčių, VLAN, bridge ar IPv6-only atveju programos „Umbrel“ nustatymuose suraskite aplinkos kintamąjį `NET_INTERFACE` ir įrašykite tikslų norimos sąsajos vardą, pvz., `enp1s0` arba `wlan0`. Išsaugokite; jei „Umbrel“ nepaleidžia programos iš naujo, paleiskite ją iš naujo per sąsają. Nespėkite, kad visur sąsaja vadinasi `eth0`.

Matuojama viena sąsaja, kad Docker tiltų ir fizinio tinklo srautas nebūtų sudėtas ir suskaičiuotas du kartus. Jei „Umbrel“ veikia virtualioje mašinoje, rodoma tos VM tinklo sąsaja. Visos fizinio serverio ar maršrutizatoriaus įrangos srautas nebus matomas.

## Rodmenų reikšmė ir patikra

- RX – į „Umbrel“ gaunami duomenys, TX – iš jo išsiunčiami.
- Greitis = baitų skaitiklio pokytis × 8 / realiai praėjęs laikas / 1 000 000, vienetas Mbps. **8 Mbps = 1 MB/s**.
- Mėginiai imami kas 2 sekundes; tai trumpalaikis vidutinis greitis, ne nenutrūkstamas srautas. Fone naršyklė gali pristabdyti valdiklio užklausas.
- Rodomas LAN ir interneto srautas kartu. Tai nėra interneto spartos testas.
- Pradžioje, pasikeitus sąsajai, nusinulinus skaitikliams arba sustojus matuokliui rodomas brūkšnys. Senesni nei 10 sekundžių duomenys neberodomi kaip dabartinis greitis.
- Patikrinkite įkeldami didesnį failą iš kompiuterio į „Umbrel“: turi kilti RX. Atsisiunčiant failą iš „Umbrel“ turi kilti TX. Vertinkite kelių matavimų vidurkį, o ne identiškas akimirkos reikšmes.
- Jei valdiklis tuščias, pirma atverkite pačią programą ir perskaitykite būseną. „No IPv4 default route“ reiškia, kad reikia rankiniu būdu nustatyti sąsają. „Collector data is stale“ rodo neveikiantį matuoklį; tai nėra nulinis srautas.

## Prieigos ir pašalinimas

Matuoklis naudoja `network_mode: host`, kad `/proc/net/dev` būtų HOST, o ne jo konteinerio skaitikliai. Tai sumažina tinklo izoliaciją; nors pateiktas kodas neatveria tinklo lizdų, pats host tinklo režimas nesuteikia tinklo veiksmams „tik skaitymo“ garantijos. Kodas trumpas ir pateiktas peržiūrai.

Abu procesai veikia kaip UID/GID 1000, be Linux capabilities, be privilegijų didinimo, su tik skaitoma konteinerio failų sistema ir atminties/procesų ribomis. Nėra Docker socket, host PID režimo, root naudotojo ar host disko /proc prijungimų. Rašomi tik programos būsenos duomenys. Web procesas yra atskirame įprastame konteinerio tinkle; matuoklis neatveria HTTP prievado.

Naršyklės prieigą saugo „Umbrel“ app_proxy prisijungimas. Vidinis `/widget` endpointas neturi autentifikacijos (taip jį pasiima „Umbrel“); kitos tame Docker tinkle esančios programos gali skaityti jo greičio bei sąsajų informaciją. Jis neturi rašymo ar valdymo API. Nė vienas konteineris tiesiogiai nepublikuoja host prievadų.

Naudojamas oficialus Python vaizdas, užfiksuotas manifestų indekso SHA-256. Patikrintas Docker Registry indeksas turi Linux amd64 ir arm64 vaizdus; indekso metaduomenys nurodo Python 3.13.16 / Alpine 3.24. Vaizdas užfiksuotas, todėl saugumo atnaujinimams ateityje reikės sąmoningai atnaujinti jo digest.

Pašalinimas: pašalinkite „Network Traffic“ programą per „Umbrel“ ir, jei nebereikia, jos bendruomenės parduotuvę. OS kodo atstatyti nereikia. Programos pašalinimas panaikins jos būsenos duomenis pagal įprastą „Umbrel“ pašalinimo eigą.

## Bandymų ribos

Pridedamas `test_meter.py` tikrina RX/TX stulpelius, Mbps skaičiavimą, skaitiklių nusinulinimą, maršruto metriką, rankinį sąsajos pasirinkimą, pasenusius duomenis ir JSON valdiklio formatą. Paleidimas: `python -m unittest -v test_meter.py`.

Šioje darbo aplinkoje nėra Docker / veikiančio „Umbrel“ įrenginio. Konteinerių paleidimas, galutinis darbalaukio vaizdas ir paketo gyvavimo ciklas turi būti patikrinti pirmojo diegimo metu. Tai parengtas kandidatas diegimui, o ne jau jūsų įrenginyje patvirtintas sprendimas.
