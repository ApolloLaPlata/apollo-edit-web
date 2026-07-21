import React, { useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import { LogIn, Lock, Mail, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        toast.success('Cadastro realizado! Verifique seu email se necessário, ou faça login.');
        setIsSignUp(false);
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        toast.success('Login efetuado com sucesso!');
      }
    } catch (error: any) {
      toast.error(error.message || 'Erro na autenticação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Background Orbs */}
      <div className="login-bg-orb-1"></div>
      <div className="login-bg-orb-2"></div>

      <div className="login-card">
        <div className="login-header">
          <div className="login-icon-wrap">
            <Lock />
          </div>
          <h1 className="login-title">Apollo<span>Edit</span></h1>
          <p className="login-subtitle">{isSignUp ? 'Criar Nova Conta' : 'Acesso Restrito'}</p>
        </div>

        <form onSubmit={handleAuth} className="login-form">
          <div className="input-group">
            <label>Email</label>
            <div className="input-wrapper">
              <div className="input-icon">
                <Mail size={18} />
              </div>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="login-input"
                placeholder="seu@email.com"
                required
              />
            </div>
          </div>

          <div className="input-group">
            <label>Senha</label>
            <div className="input-wrapper">
              <div className="input-icon">
                <Lock size={18} />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="login-input"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="login-btn"
          >
            {loading ? (
              <Loader2 className="spinner" />
            ) : (
              <>
                <LogIn size={20} />
                {isSignUp ? 'Cadastrar' : 'Entrar'}
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <button
            type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            className="toggle-mode-btn"
          >
            {isSignUp ? 'Já tem uma conta? Faça login' : 'Ainda não tem conta? Cadastre-se'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
