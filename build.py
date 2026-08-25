(async function migrarFornecedores() {
  if (typeof MATERIAIS_DATA === 'undefined') {
    console.error('❌ MATERIAIS_DATA não definido.');
    return;
  }
  const fornecedoresSet = new Set();
  MATERIAIS_DATA.items.forEach(item => {
    if (item.fornecedor && item.fornecedor.trim() !== '') {
      fornecedoresSet.add(item.fornecedor.trim());
    }
  });
  if (MATERIAIS_DATA.filtros && MATERIAIS_DATA.filtros.fornecedores) {
    MATERIAIS_DATA.filtros.fornecedores.forEach(f => {
      if (f && f.trim() !== '') fornecedoresSet.add(f.trim());
    });
  }
  const fornecedores = Array.from(fornecedoresSet).sort();
  console.log(`📦 ${fornecedores.length} fornecedores únicos encontrados.`);
  const snapshot = await db.collection('fornecedores').get();
  const existing = new Set(snapshot.docs.map(doc => doc.data().nome));
  console.log(`📊 ${existing.size} fornecedores já cadastrados.`);
  const toAdd = fornecedores.filter(f => !existing.has(f));
  if (toAdd.length === 0) {
    console.log('✅ Todos os fornecedores já estão no Firestore.');
    return;
  }
  console.log(`➕ Adicionando ${toAdd.length} novos fornecedores...`);
  const batch = db.batch();
  for (const nome of toAdd) {
    const docRef = db.collection('fornecedores').doc();
    batch.set(docRef, { nome, contato: '', telefone: '', email: '', obs: '' });
  }
  await batch.commit();
  console.log(`✅ ${toAdd.length} fornecedores migrados com sucesso!`);
})();
