# Projekt Dictaphone (fka Diktiergeraet)

🦜🦜 Dictaphone 

Erstelle eigenes Diktiergeraet, mit dem ich Sprachnachrichten dokumentieren und zusammenfassen kann.

*Use Case:* Ich diktiere Gesprächsnotizen oder sonstige Gedanken in mein Handy. Es wird eine Zusammenfassung und ein Transkript erstellt.
- Zusammenfassung und Transkript werden inklusive Timestamp per Email an mich geschickt
- Zusammenfassung und Transkript werden einem Google Document hinzugefügt. Dabei wird stets das gleiche Google Doc genutzt, so dass ein Log entsteht. Neue Einträge kommen nach oben, so dass alle Einträge gegenchronologisch sind. Als Header für jeden Eintrag wird der Timestamp der Diktion genutzt sowie ein beschreibendes Schlagwort (Gesprächspartner, Kern der Notiz, etc) 

# Sprachmemo-Pipeline: Infrastruktur, Kosten, Roadmap

Ein selbst gehosteter Workflow: Sprachmemo per Mail einsprechen, automatisch
transkribieren, von Claude zusammenfassen lassen, Ergebnis als E-Mail erhalten
und in einem fortlaufenden Google Doc protokollieren. Alles auf eigener
Infrastruktur, damit die Inhalte und das verknüpfte Google-Konto unter eigener
Kontrolle bleiben.

Grundsatzentscheidungen: eigener VPS statt Cloud-Automatisierung, Transkription
auf dem eigenen Server statt bei einem Drittdienst, langsame Verarbeitung
ausdrücklich akzeptiert (Ziel ist Dokumentation und spätere Verfügbarkeit, nicht
Geschwindigkeit).

## Benötigte Infrastruktur

| Komponente | Einrichtung | Laufend | Zweck |
|---|---|---|---|
| Dediziertes Google-Konto | selbst anlegen | – | Gmail-Trigger und Versand, Google Doc als Log. Trennt die Automatisierung vom privaten Konto |
| VPS (Hetzner Cloud, Linux) | mieten, absichern | läuft 24/7 | trägt alle Dienste, immer erreichbar |
| Docker und docker-compose | installieren | – | Dienste isoliert und reproduzierbar betreiben |
| n8n (im Docker) | aufsetzen | läuft dauerhaft | Orchestrierung der Pipeline |
| Whisper ASR-Container | aufsetzen | läuft, arbeitet bei Bedarf | Transkription Audio zu Text, per HTTP aus n8n aufgerufen |
| Caddy (Reverse Proxy + TLS) | konfigurieren | läuft dauerhaft | HTTPS, zwingend für Google-OAuth |
| Subdomain `n8n.tillmannlang.com` | DNS-A-Eintrag bei GoDaddy | – | Adresse für TLS und OAuth-Rückruf. Bestehende Domain, kein Kauf |
| Google-Cloud-Projekt | OAuth-Zugangsdaten erzeugen | – | kontrollierter Zugriff auf Gmail und Docs mit minimalen Scopes |
| Anthropic-API-Konto + Guthaben | anlegen, aufladen | pro Nutzung | Zusammenfassung via Claude-API |

Zusammenspiel: Memo per Mail eintreffen lassen, n8n erkennt sie, Whisper
transkribiert, Claude fasst zusammen, n8n verschickt die Mail und hängt den
Eintrag ans Google Doc an.

## Kostentreiber

| Treiber | Größenordnung | Anmerkung |
|---|---|---|
| VPS (Hauptkosten) | rund 5 bis 8 EUR/Monat [unverified] | Modell mit etwas RAM-Reserve für Whisper, bleibt unter dem 10-EUR-Deckel |
| Domain | 0 EUR zusätzlich | `tillmannlang.com` bereits vorhanden, nur ein Subdomain-Eintrag |
| Anthropic-API (Zusammenfassung) | Bruchteile Cent bis Cent pro Memo | vernachlässigbar |
| Whisper (Transkription) | 0 EUR pro Nutzung | verbraucht nur VPS-Rechenzeit |
| Claude-Pro-Abo | hier nicht nutzbar | API wird getrennt abgerechnet, nicht über das Abo |
| Eigene Zeit | der eigentliche Aufwand | siehe Roadmap |

Die EUR-Beträge sind grobe Orientierung und vor der Bestellung beim Anbieter zu
prüfen. Einzig nennenswerte laufende Geldkosten: der VPS. Alles andere bewegt
sich im Cent-Bereich oder ist null.

Hinweis zur Transkriptionsleistung: Whisper auf CPU ist rechenintensiv. Mit
kleinem Modell dauert eine kurze Memo eher Minuten als Sekunden. Das ist hier
bewusst akzeptiert. Reicht es später nicht, ist der Wechsel auf eine
Cloud-Transkription der Fallback, dann allerdings mit einem Drittanbieter, der
das Audio sieht.

# Dev Status per Jul 1

# Sprachmemo-Pipeline: Roadmap und Fortschritt

Selbst gehosteter Workflow: Sprachmemo per Mail einsprechen, auf eigenem Server
transkribieren (Whisper), von Claude zusammenfassen lassen, Ergebnis als E-Mail
erhalten und in einem fortlaufenden Google Doc protokollieren.

Stand: Session 2b abgeschlossen, Session 3 begonnen. n8n läuft über HTTPS, der
E-Mail-Trigger holt Memos samt Audio-Anhang. Als Nächstes: Whisper.

## Übersicht

| Session | Inhalt | Status |
|---|---|---|
| 1 | Konten und Fundament | abgeschlossen |
| 2a | Server absichern und Docker | abgeschlossen |
| 2b | n8n über HTTPS | abgeschlossen |
| 3 | Trigger und Transkription | teilweise (Trigger fertig, Whisper offen) |
| 4 | Zusammenfassung und Ausgabe | offen |
| 5 | Feinschliff | offen |

## Eckdaten der Infrastruktur

| Element | Wert |
|---|---|
| Server | Hetzner Cloud CX22, Ubuntu 26.04 LTS |
| Öffentliche IP | 178.104.138.236 |
| Subdomain | n8n.tillmannlang.com |
| Zugang | SSH nur per Schlüssel, Benutzer `tillmann`, Root gesperrt |
| Firewall | ufw aktiv (SSH, 80, 443) |
| Container | Docker + compose; laufend: n8n, Caddy |
| n8n-Verzeichnis | `~/n8n` (docker-compose.yml, Caddyfile) |
| n8n-URL | https://n8n.tillmannlang.com (TLS via Caddy/Let's Encrypt) |
| Empfangspostfach | dediziertes Gmail (auch Admin-Konto für n8n, Hetzner) |
| Gmail-Label | `dictaphone-memos` (Filter: An mich + Anhang, Posteingang übersprungen) |
| Mail-Zugang für n8n | IMAP + App-Passwort (imap.gmail.com:993, SSL) |

Login: `ssh tillmann@178.104.138.236`

---

## Session 1 — Konten und Fundament (abgeschlossen)

Ziel-Status: Server existiert, per SSH erreichbar, Subdomain zeigt darauf.

| Schritt | Ziel-Status | Status |
|---|---|---|
| Dediziertes Google-Konto | eigenes Konto für die Automatisierung | erledigt |
| Anthropic-Console-Konto + Guthaben | API-Konto bereit (Key folgt Session 4) | erledigt |
| Hetzner-Cloud-Konto | Cloud-Bereich nutzbar | erledigt |
| SSH-Schlüssel auf dem Mac | Schlüsselpaar erzeugt | erledigt |
| VPS erstellen | CX22/Ubuntu läuft, IP bekannt | erledigt |
| DNS-A-Eintrag bei GoDaddy | Subdomain löst auf die IP auf | erledigt |
| Erster SSH-Login | Verbindung steht | erledigt |

## Session 2a — Server absichern und Docker (abgeschlossen)

Ziel-Status: Server gehärtet, nur Schlüssel-Login als Nicht-Root, Docker bereit.

| Schritt | Ziel-Status | Status |
|---|---|---|
| System aktualisieren | Sicherheitslücken geschlossen | erledigt |
| Nicht-Root-Benutzer + sudo | Alltagsbenutzer `tillmann` | erledigt |
| SSH-Schlüssel für den Benutzer | Schlüssel-Login als `tillmann` | erledigt |
| Gate: neuen Login testen | Ersatz-Zugang nachgewiesen | erledigt |
| Root-/Passwort-Login abschalten | nur Schlüssel-Login, Root gesperrt | erledigt |
| Firewall (ufw) | nur SSH, 80, 443 offen | erledigt |
| Docker + compose | Container ohne sudo startbar | erledigt |

## Session 2b — n8n über HTTPS (abgeschlossen)

Ziel-Status: n8n-Login sicher erreichbar mit gültigem Zertifikat.

| Schritt | Ziel-Status | Status |
|---|---|---|
| Projektordner + docker-compose.yml | n8n + Caddy definiert | erledigt |
| Caddyfile | Weiterleitung Domain zu n8n:5678 | erledigt |
| Container starten | n8n und Caddy laufen | erledigt |
| TLS-Zertifikat | HTTPS via Let's Encrypt aktiv (per curl bestätigt) | erledigt |
| n8n Owner-Konto | Login angelegt, Canvas erreichbar | erledigt |

---

## Session 3 — Trigger und Transkription (teilweise)

Ziel-Status: Memo per Mail senden, Transkript erscheint als Text in n8n.

| Schritt | Ziel-Status | Status |
|---|---|---|
| Gmail-Label + Filter | Memos landen automatisch im Label `dictaphone-memos` | erledigt |
| App-Passwort | IMAP-Zugang für n8n eingerichtet | erledigt |
| IMAP-Trigger in n8n | Trigger liest das Label, lädt den `.m4a`-Anhang | erledigt |
| Trigger getestet | Test-Memo samt Audio-Anhang erscheint in n8n | erledigt |
| Whisper-Container | Transkriptionsdienst läuft auf dem Server | offen, als Nächstes |
| Audio zu Text verdrahten | n8n schickt Audio an Whisper, erhält Transkript | offen |

## Session 4 — Zusammenfassung und Ausgabe (offen)

Ziel-Status: End-to-End. Memo rein, Mail mit Zusammenfassung + Transkript raus, Eintrag im Google Doc.

| Schritt | Ziel-Status |
|---|---|
| Anthropic-API-Key | Key erzeugt und in n8n hinterlegt |
| Zusammenfassung via Claude | Transkript wird zu einer Zusammenfassung |
| Google-Cloud-OAuth | n8n darf mit minimalen Rechten auf Gmail und Docs zugreifen |
| Versand per Gmail | Zusammenfassung + Transkript + Zeitstempel als Mail |
| Anhängen ans Google Doc | Eintrag mit Zeitstempel als Überschrift im selben Dokument |

## Session 5 — Feinschliff (offen)

Ziel-Status: Pipeline läuft zuverlässig im Alltag.

| Schritt | Ziel-Status |
|---|---|
| iOS-Kurzbefehl (Shortcut) | ein Tipp: aufnehmen und an die feste Adresse senden |
| Zeitstempel-Format | saubere Überschrift pro Eintrag |
| Immer dasselbe Doc | fortlaufendes Log statt vieler Einzeldokumente |
| Sonderfälle abfangen | z.B. Mail ohne `.m4a`-Anhang wird sauber ignoriert |
| Schutz gegen Doppelverarbeitung | jede Memo genau einmal verarbeitet |
| Gesamttest | mehrere Memos durchgespielt, stabil |

---

## iPhone-Ablauf (geplant, Detail in Session 5)

1. Apple Sprachmemos aufnehmen.
2. Teilen zu Mail zu an die dedizierte Adresse (`.m4a`-Anhang).
3. Gmail-Filter sortiert ins Label `dictaphone-memos`.
4. Später ersetzt ein iOS-Shortcut die Schritte 1 und 2 durch einen Tipp.

## Wiedereinstieg nächste Session

1. Terminal: `ssh tillmann@178.104.138.236` (Prompt muss `tillmann@...` zeigen).
2. Prüfen, dass die Container laufen: `docker ps` (n8n, caddy sollten „Up" sein).
3. n8n im Browser öffnen: https://n8n.tillmannlang.com
4. Weiter mit Session 3, nächster Schritt: Whisper-Container aufsetzen und Audio zu Text verdrahten.

## Offene Hinweise

- Server wird stündlich abgerechnet, solange er existiert. Nur Löschen stoppt die Kosten.
- Anthropic-API-Key erst in Session 4 erzeugen, da er nur einmal angezeigt wird.
- Whisper läuft auf CPU mit kleinem Modell. Transkription dauert eher Minuten als Sekunden, bewusst akzeptiert.
- `:latest` als Image-Tag ist fürs Lernen ok; für stabilen Betrieb später feste Versionen pinnen.
