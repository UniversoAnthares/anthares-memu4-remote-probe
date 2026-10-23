<!-- BEGIN ANTHARES DOCUMENTATION REQUIRED -->
# Documentação permanente do titular — Universo Anthares
Antes de qualquer tarefa, retomada ou delegação, leia as regras obrigatórias e o índice da documentação central privada: https://github.com/UniversoAnthares/anthares-governance (REGRAS-OBRIGATORIAS.md, INDICE.md e seções aplicáveis de PROMPT-MESTRE.md).
No computador Anthares, a fonte está em D:\AntharsWork\governance; há cópia local em docs/anthares. Fora dele, use o conector GitHub ou acesso Git autorizado à fonte privada. Não exponha o inventário interno neste repositório público. Se faltar acesso, não presuma o conteúdo: registre a barreira e continue partes independentes.
Registre versão/hash no job, sem narrar a leitura ao usuário. Preserve instruções locais, Test Hub, locks, provas e propriedade dos arquivos.
Trabalhe com concisão, oculto e sem áudio; não use mouse, teclado ou clipboard pessoais. Feche imediatamente após o último uso todos os recursos temporários próprios, com identificação de dono e limpeza em finally; preserve serviços ativos compartilhados e trabalho pessoal.
Remoto: Anthares Remote/ARA > WinRemote > Remote Desktop Commander > MeshCentral > AI Commander; avance com evidência. Navegação interativa: Anthares Browser > Browserless > TinyFish; TinySearch/TinyFetch primeiro nos contratos de pesquisa Lovecraft/leitura pública. Código: GitHub > GitLab > Codeberg, sem trocar primários de execução por inferência.
Não desative publicadores, agentes ou Git. Coordene redundância, exclusão mútua e reconciliação antes de reenviar. Falha técnica permite alternativa autorizada; recusa de segurança/aprovação não permite contorno.
Estas instruções não ampliam permissões nem substituem políticas superiores.
<!-- END ANTHARES DOCUMENTATION REQUIRED -->

# UNIVERSO ANTHARES — REGRA PERMANENTE PARA TODOS OS AGENTES (21/10/2026)

## Janelas e abas: fechamento obrigatório após cada uso

Qualquer agente Anthares com permissão para abrir janelas, navegadores, abas, terminais, caixas de diálogo ou interfaces de emuladores deve encerrar **imediatamente após o uso** cada recurso temporário que criou. A regra vale para sucesso, erro, timeout, cancelamento, falha do controlador, reinício e recuperação. Não acumular janelas entre operações.

Contrato obrigatório para cada implementação:
1. Registre na criação o proprietário do recurso (job/agente), PID e hora de início, HWND ou CDP target ID.
2. Reutilize sessões e serviços de navegador em segundo plano quando necessários. Toda aba temporária deve ser fechada no `finally` da operação. Mantenha navegador automatizado invisível e sem áudio.
3. Feche também janelas PowerShell, CMD, interfaces web, navegador, painéis temporários e emuladores abertos pelo agente após a tarefa terminar. Preserve somente serviços/VMs que ainda prestam serviço ativo, sem janelas temporárias remanescentes.
4. Refaça a limpeza por meio de watchdog em caso de interrupção. A limpeza deve reconhecer de maneira positiva a propriedade do recurso antes de fechá-lo.
5. Nunca encerre indiscriminadamente processos por nome nem feche abas pessoais, documentos não salvos, sessões de outros agentes ou recursos compartilhados ainda utilizados.
6. A última referência de uso determina o fechamento de um recurso compartilhado. O fim de uma operação determina o fechamento imediato de suas próprias janelas temporárias.
7. Audite recursos criados, fechados, órfãos recuperados e erros de fechamento. Novo agente/launcher só entra em operação quando implementar esse ciclo de vida ou mecanismo equivalente.

Windows local: `D:\AntharsWork\agent-window-policy\WINDOW_LIFECYCLE_POLICY.md`; execução: `window_guard.py`; recuperação agendada: `Anthares Agent Window Lifecycle Guard`. Para abas CDP do CORTES, consulte `cortes-tab-lifecycle.mjs`.

Esta política deve ser repassada a agentes delegados, sessões Claude/Claude Code, Codex, Copilot, Kilo, Cline e qualquer executor presente ou futuro. A norma escrita não substitui a instrumentação de cada controlador; certifique-se de que a implementação foi aplicada e testada antes de declarar cobertura total.

A prioridade de controle remoto já estabelecida permanece: Anthares Remote > WinRemote > Remote Desktop Commander > MeshCentral > AI Commander.