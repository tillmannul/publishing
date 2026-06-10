# Projekt: Diktiergeraet

🦜🦜  Diktiergeraet

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

## Roadmap mit Breakpoints

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
