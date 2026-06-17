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

# Dev Status per Jun 17

Selbst gehosteter Workflow: Sprachmemo per Mail einsprechen, auf eigenem Server
transkribieren (Whisper), von Claude zusammenfassen lassen, Ergebnis als E-Mail
erhalten und in einem fortlaufenden Google Doc protokollieren.

Stand: Session 2a abgeschlossen. Server steht, ist abgesichert, Docker läuft.

### Übersicht

| Session | Inhalt | Status |
|---|---|---|
| 1 | Konten und Fundament | abgeschlossen |
| 2a | Server absichern und Docker | abgeschlossen |
| 2b | n8n über HTTPS | offen, als Nächstes |
| 3 | Trigger und Transkription | offen |
| 4 | Zusammenfassung und Ausgabe | offen |
| 5 | Feinschliff | offen |

### Eckdaten der Infrastruktur

| Element | Wert |
|---|---|
| Server | Hetzner Cloud CX22, Ubuntu 26.04 LTS |
| Öffentliche IP | 178.104.138.236 |
| Subdomain | n8n.tillmannlang.com (A-Record bei GoDaddy) |
| Zugang | SSH nur per Schlüssel, Benutzer `tillmann`, Root-Login gesperrt |
| Firewall | ufw aktiv, offen: SSH, 80, 443 |
| Container | Docker + docker compose installiert |

Login von einem neuen Terminal: `ssh tillmann@178.104.138.236`

---

### Session 1 — Konten und Fundament (abgeschlossen)

Ziel-Status: Server existiert, ist per SSH erreichbar, Subdomain zeigt darauf.

| Schritt | Ziel-Status | Status |
|---|---|---|
| Dediziertes Google-Konto | eigenes Konto für die Automatisierung vorhanden | erledigt |
| Anthropic-Console-Konto + Guthaben | API-Konto mit Guthaben bereit (Key folgt in Session 4) | erledigt |
| Hetzner-Cloud-Konto | Cloud-Bereich mit Projektzugang nutzbar | erledigt |
| SSH-Schlüssel auf dem Mac | Schlüsselpaar erzeugt, privater Schlüssel bleibt lokal | erledigt |
| VPS erstellen | CX22 mit Ubuntu läuft, IP bekannt | erledigt |
| DNS-A-Eintrag bei GoDaddy | n8n.tillmannlang.com löst auf die Server-IP auf | erledigt |
| Erster SSH-Login | Verbindung zum Server steht | erledigt |

### Session 2a — Server absichern und Docker (abgeschlossen)

Ziel-Status: Server gehärtet, nur Schlüssel-Login als Nicht-Root, Docker einsatzbereit.

| Schritt | Ziel-Status | Status |
|---|---|---|
| System aktualisieren | bekannte Sicherheitslücken geschlossen | erledigt |
| Nicht-Root-Benutzer + sudo | Alltagsbenutzer `tillmann` mit Adminrechten bei Bedarf | erledigt |
| SSH-Schlüssel für den Benutzer | Login als `tillmann` per Schlüssel möglich | erledigt |
| Gate: neuen Login testen | Ersatz-Zugang nachweislich funktionsfähig | erledigt |
| Root- und Passwort-Login abschalten | nur noch Schlüssel-Login als `tillmann`, Root gesperrt | erledigt |
| Firewall (ufw) | nur SSH, 80, 443 offen, Rest zu | erledigt |
| Docker + compose | Container lassen sich ohne sudo starten | erledigt |

---

### Session 2b — n8n über HTTPS (offen, als Nächstes)

Ziel-Status: n8n-Login sicher erreichbar unter https://n8n.tillmannlang.com mit gültigem Zertifikat.

| Schritt | Ziel-Status |
|---|---|
| Projektordner und docker-compose-Datei | Struktur für die Container steht |
| n8n-Container | n8n läuft als Container |
| Caddy als Reverse Proxy | Anfragen werden an n8n weitergereicht |
| TLS-Zertifikat | automatisches HTTPS via Let's Encrypt aktiv |
| Test im Browser | n8n-Login öffnet sich verschlüsselt über die Subdomain |

### Session 3 — Trigger und Transkription (offen)

Ziel-Status: Memo per Mail senden, Transkript erscheint als Text in n8n.

| Schritt | Ziel-Status |
|---|---|
| n8n-Grundlagen | erster Workflow verstanden und angelegt |
| IMAP-Trigger | n8n erkennt neue Memo-Mails im Postfach |
| Whisper-Container | Transkriptionsdienst läuft auf dem Server |
| Audio zu Text verdrahten | n8n schickt Audio an Whisper, erhält Text zurück |

### Session 4 — Zusammenfassung und Ausgabe (offen)

Ziel-Status: End-to-End. Memo rein, Mail mit Zusammenfassung und Transkript raus, Eintrag im Google Doc.

| Schritt | Ziel-Status |
|---|---|
| Anthropic-API-Key | Key erzeugt und in n8n hinterlegt |
| Zusammenfassung via Claude | Transkript wird zu einer Zusammenfassung |
| Google-Cloud-OAuth | n8n darf mit minimalen Rechten auf Gmail und Docs zugreifen |
| Versand per Gmail | Zusammenfassung + Transkript + Zeitstempel als Mail an dich |
| Anhängen ans Google Doc | Eintrag mit Zeitstempel als Überschrift im selben Dokument |

### Session 5 — Feinschliff (offen)

Ziel-Status: Pipeline läuft zuverlässig im Alltag.

| Schritt | Ziel-Status |
|---|---|
| Zeitstempel-Format | saubere Überschrift pro Eintrag |
| Immer dasselbe Doc | fortlaufendes Log statt vieler Einzeldokumente |
| Schutz gegen Doppelverarbeitung | jede Memo wird genau einmal verarbeitet |
| Gesamttest | mehrere Memos durchgespielt, Ergebnis stabil |

---

### Wiedereinstieg vor der nächsten Session

1. Neues Terminal, einloggen: `ssh tillmann@178.104.138.236`
2. Prompt muss `tillmann@...` zeigen, nicht root.
3. Weiter mit Session 2b: Projektordner und docker-compose-Datei.

### Offene Hinweise

- Server wird stündlich abgerechnet, solange er existiert. Ausschalten stoppt die Kosten nicht, nur Löschen.
- Anthropic-API-Key erst in Session 4 erzeugen, da er nur einmal angezeigt wird.
- Whisper läuft auf CPU mit kleinem Modell. Transkription dauert eher Minuten als Sekunden, bewusst akzeptiert.

## (veraltet) Original Roadmap mit Breakpoints

Aufgeteilt in fünf Sessions. Jede endet an einem stabilen, testbaren Zustand, an
dem problemlos pausiert werden kann. Gesamtaufwand realistisch 1,5 bis 2 Tage,
über mehrere Termine verteilt.

### Session 1 — Konten und Fundament

| Punkt | Inhalt |
|---|---|
| Aufgaben | Google-Konto anlegen, Anthropic-API-Konto + kleines Guthaben, VPS bei Hetzner mieten, DNS-A-Eintrag bei GoDaddy auf die Server-IP |
| Lernfokus | Bestellvorgänge, DNS-Grundlagen |
| Breakpoint | Server per SSH erreichbar, `n8n.tillmannlang.com` löst auf die Server-IP auf |
| Zeit | rund 1 bis 2 Stunden |

### Session 2a — Server absichern und Docker

| Punkt | Inhalt |
|---|---|
| Aufgaben | SSH-Zugang, Grundabsicherung (Firewall, kein Root-Login, Updates), Docker und docker-compose installieren |
| Lernfokus | Linux-Server, Grundabsicherung, Docker |
| Breakpoint | Server abgesichert, Docker läuft, Testcontainer startet |
| Zeit | rund 2 bis 3 Stunden |

### Session 2b — n8n über HTTPS

| Punkt | Inhalt |
|---|---|
| Aufgaben | Caddy als Reverse Proxy mit automatischem TLS, n8n im Docker dahinter |
| Lernfokus | Reverse Proxy, TLS-Zertifikate, docker-compose |
| Breakpoint | n8n-Login erreichbar unter `https://n8n.tillmannlang.com` mit gültigem Zertifikat |
| Zeit | rund 2 bis 3 Stunden |

### Session 3 — Trigger und Transkription

| Punkt | Inhalt |
|---|---|
| Aufgaben | n8n-Grundlagen, IMAP-Trigger auf das Memo-Postfach, Whisper-Container aufsetzen, Audio per HTTP-Knoten transkribieren |
| Lernfokus | n8n-Workflows, Container, Verdrahtung, Debugging |
| Breakpoint | Memo per Mail senden, Transkript erscheint als Text in n8n |
| Zeit | rund 3 bis 4 Stunden |

### Session 4 — Zusammenfassung und Ausgabe

| Punkt | Inhalt |
|---|---|
| Aufgaben | Claude-API-Knoten für die Zusammenfassung, Google-Cloud-OAuth einrichten, Versand per Gmail, Anhängen ans Google Doc |
| Lernfokus | API-Aufrufe, OAuth, Scopes |
| Breakpoint | End-to-End: Memo rein, Mail mit Zusammenfassung + Transkript raus, Eintrag im Google Doc |
| Zeit | rund 3 bis 4 Stunden |

### Session 5 — Feinschliff

| Punkt | Inhalt |
|---|---|
| Aufgaben | Zeitstempel als Überschrift, stets dasselbe Google Doc, Robustheit gegen Doppelverarbeitung, Gesamttest |
| Lernfokus | Ablauflogik, Idempotenz |
| Breakpoint | Pipeline läuft zuverlässig im Alltag |
| Zeit | rund 1 bis 2 Stunden |

Die fummeligsten Teile mit dem höchsten Lernwert und der größten
Frustrationsgefahr sind Session 2b (TLS, Proxy) und Session 4 (OAuth, Scopes).
Dort lohnt sich Geduld und schrittweises Testen am meisten.
