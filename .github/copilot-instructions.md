# Universo Anthares — instruções obrigatórias para Copilot

Leia e siga o `AGENTS.md` da raiz deste repositório. Regra permanente do proprietário, 21/10/2026: toda janela temporária, aba de navegador, console PowerShell/CMD e diálogo criado por um agente deve ser **fechado imediatamente após o uso**, inclusive em falha, timeout e interrupção.

Registre proprietário e identidade do recurso na criação; feche no `finally`; recupere órfãos identificados por watchdog; execute navegadores de automação invisíveis e sem áudio, fechando as abas temporárias após cada operação. Proteja as janelas pessoais do usuário, trabalhos não salvos e recursos compartilhados ainda ativos. Proibido `taskkill` genérico em navegadores e serviços. Exija esse contrato também de scripts e subagentes gerados pelo Copilot. Referência central: https://github.com/UniversoAnthares/home/blob/main/AGENTS.md.
