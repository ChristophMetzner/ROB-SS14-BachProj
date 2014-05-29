ROB-SS14-BachProj
=================

Optimierung biologisch-realistischer Neuronenmodelle

# Installation

Benötigte Software: java, python2.7, SciPy, NumPy, matplotlib, NEURON, inspyred
Lokale Konfigurationen:
- Zu den Globalen Variablen muss der Pfad zu neuroConstruct_1.6.0 hinzugefügt werden.
  Unter Linux einfach "export NC_HOME=PfadZuNeuroconstruct" in die .bashrc einfügen.
  So kann jeder mit der gleichen nC.sh oder nC.bat arbeiten.
- NeuroConstruct muss so konfiguriert werden, dass NEURON gefunden wird. Dazu NeuroConstruct öffnen und unter allgemeine Einstellungen gehen.

# Ausführung

Der Genetische Algorithmus kann mit multiEA.py eingestellt und ausgeführt werden.

    python2.7 multiEA.py

Über den Befehl

    python2.7 -m cProfile -s time multiEA.py

Lässt sich der Profiler anhängen.