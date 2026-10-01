import { defineConfig, Plugin } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Issue 82: the landing App still gates Free research and encounter help on login.
 * Rewrite those call sites at compile time so guests hit POST /public/rights-assistant
 * and GET /public/encounter. Private /cases routes stay on authApi.
 */
function guestPublicRightsRewrite(): Plugin {
  return {
    name: 'guest-public-rights-rewrite',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('/src/App.tsx')) return null;
      let next = code;
      if (!next.includes("from'./guestPublic'") && !next.includes('from "./guestPublic"')) {
        next = next.replace(
          "from'lucide-react';",
          "from'lucide-react';\nimport{guestEncounterReply,guestRightsAndEncounter}from'./guestPublic';",
        );
      }
      next = next.replace(
        "async function runResearch(e?:FormEvent){e?.preventDefault();if(!user){setMode('register');setAuthOpen(true);setNotice('Create a free account or sign in to use AI legal research.');return}if(!paid){setPaywallOpen(true);return}if(!q.trim()){setNotice('Enter a Georgia legal question first.');return}",
        "async function runResearch(e?:FormEvent){e?.preventDefault();if(!q.trim()){setNotice('Enter a Georgia legal question first.');return}",
      );
      next = next.replace(
        `const [answer,researchResult]=await Promise.all([
    authApi('/public/ask',{method:'POST',body:JSON.stringify({question:q.trim()})}),
    authApi('/public/research?q='+encodeURIComponent(q.trim()))
   ]);
   setAiAnswer(answer);setResearch(researchResult);`,
        `const {answer,research}=await guestRightsAndEncounter(API,api,q.trim());
   setAiAnswer(answer);setResearch(research);`,
      );
      next = next.replace(
        "const data=await authApi('/public/ask',{method:'POST',body:JSON.stringify({question:prompt})});\n   setEncounterReply(data.answer||suggestedReply(heard,scenario));",
        "const data=await guestEncounterReply(api,prompt);\n   setEncounterReply(data.answer||suggestedReply(heard,scenario));",
      );
      next = next.replace(
        "function openPolice(){if(!user){setMode('register');setAuthOpen(true);setNotice('Create a free account or sign in to use AI encounter assistance.');return}if(!paid){setPaywallOpen(true);return}setTool('police')}",
        "function openPolice(){setTool('police')}",
      );
      next = next.replace(
        "function openRights(next:ScenarioKey=scenario){setScenario(next);if(!paid){setPaywallOpen(true);return}setTool('avoid')}",
        "function openRights(next:ScenarioKey=scenario){setScenario(next);setTool('avoid')}",
      );
      return next === code ? null : next;
    },
  };
}

export default defineConfig({
  plugins: [react(), guestPublicRightsRewrite()],
});
