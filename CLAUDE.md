# Claude / Claude Code — Universo Anthares

Antes de controlar o Windows, abrir navegador, aba, PowerShell, CMD, diálogo ou interface de emulador, leia e cumpra integralmente [AGENTS.md](AGENTS.md), em especial a seção de fechamento obrigatório de janelas do agente (regra do proprietário de 21/10/2026).

**Cada janela ou aba temporária aberta pelo agente deve ser fechada imediatamente após o uso**, com sucesso, erro ou cancelamento. Registre a propriedade do recurso; encerre no `finally`; restaure a limpeza de recursos órfãos por watchdog. Nunca encerre janelas pessoais, documentos não salvos, outros agentes ou serviços compartilhados ativos. Reutilize navegadores isolados, invisíveis e silenciados e feche cada aba temporária após a operação. Repasse a exigência a subagentes.

Consulte a política central em https://github.com/UniversoAnthares/home/blob/main/AGENTS.md e, no PC autorizado, `D:\AntharsWork\agent-window-policy\WINDOW_LIFECYCLE_POLICY.md`.

A ordem obrigatória de provedores continua: Anthares Remote > WinRemote > Remote Desktop Commander > MeshCentral > AI Commander.
