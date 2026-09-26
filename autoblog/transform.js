module.exports = function(fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  function makeEnclosingFunctionAsync(path) {
    let parent = path.parent;
    while (parent) {
      if (
        parent.node.type === 'FunctionDeclaration' ||
        parent.node.type === 'ArrowFunctionExpression' ||
        parent.node.type === 'FunctionExpression' ||
        parent.node.type === 'ObjectMethod' ||
        parent.node.type === 'ClassMethod'
      ) {
        if (!parent.node.async) {
          parent.node.async = true;
        }
        break; // Stop at the first enclosing function
      }
      parent = parent.parent;
    }
  }

  // Encontra chamadas a db.prepare(...).all(), .get(), .run()
  root.find(j.CallExpression, {
    callee: {
      type: 'MemberExpression',
      object: {
        type: 'CallExpression',
        callee: {
          type: 'MemberExpression',
          object: { name: 'db' },
          property: { name: 'prepare' }
        }
      },
      property: (prop) => ['all', 'get', 'run'].includes(prop.name)
    }
  }).forEach(path => {
    if (path.parent.node.type !== 'AwaitExpression') {
      const awaitExpr = j.awaitExpression(path.node);
      path.replace(awaitExpr);
      makeEnclosingFunctionAsync(path);
    }
  });

  // Encontra chamadas a db.exec(...)
  root.find(j.CallExpression, {
    callee: {
      type: 'MemberExpression',
      object: { name: 'db' },
      property: { name: 'exec' }
    }
  }).forEach(path => {
    if (path.parent.node.type !== 'AwaitExpression') {
      const awaitExpr = j.awaitExpression(path.node);
      path.replace(awaitExpr);
      makeEnclosingFunctionAsync(path);
    }
  });

  return root.toSource();
};
