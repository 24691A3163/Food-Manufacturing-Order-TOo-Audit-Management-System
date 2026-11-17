import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/layout/Sidebar';
import { TopNav } from './components/layout/TopNav';
import { OwnerDashboard } from './pages/dashboard/OwnerDashboard';
import { SalesmanPortal } from './pages/orders/SalesmanPortal';
import { InvoicesManagement } from './pages/invoices/InvoicesManagement';
import { ProductionManagement } from './pages/production/ProductionManagement';
import { InventoryManagement } from './pages/inventory/InventoryManagement';
import { PurchasesManagement } from './pages/purchases/PurchasesManagement';
import { CostingManagement } from './pages/costing/CostingManagement';
import { PaymentsManagement } from './pages/payments/PaymentsManagement';
import { AuditReports } from './pages/reports/AuditReports';
import { BenchmarkRunner } from './pages/benchmark/BenchmarkRunner';
import { api } from './services/api';

const MainLayout: React.FC = () => {
  const { role } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('benchmark');
  const [isBenchmarkRunning, setIsBenchmarkRunning] = useState<boolean>(false);
  const [varianceAlertCount, setVarianceAlertCount] = useState<number>(1);

  // When role changes, align default tab intelligently
  useEffect(() => {
    if (role === 'salesman') {
      setCurrentTab('salesman-portal');
    } else if (role === 'production') {
      setCurrentTab('production');
    } else if (role === 'auditor') {
      setCurrentTab('reports');
    }
  }, [role]);

  const handleRunBenchmark = async () => {
    setIsBenchmarkRunning(true);
    try {
      await api.runBenchmark();
      setCurrentTab('benchmark');
    } catch (e) {
      console.error('Benchmark execution error:', e);
    } finally {
      setIsBenchmarkRunning(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Collapsible Enterprise Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        varianceAlertCount={varianceAlertCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header with Role Switcher & Benchmark Action */}
        <TopNav
          onRunBenchmark={handleRunBenchmark}
          isBenchmarkRunning={isBenchmarkRunning}
        />

        {/* Dynamic Screen View */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          {currentTab === 'dashboard' && <OwnerDashboard onNavigate={setCurrentTab} />}
          {currentTab === 'salesman-portal' && <SalesmanPortal />}
          {currentTab === 'orders' && <SalesmanPortal />}
          {currentTab === 'invoices' && <InvoicesManagement />}
          {currentTab === 'production' && <ProductionManagement />}
          {currentTab === 'inventory' && <InventoryManagement />}
          {currentTab === 'purchases' && <PurchasesManagement />}
          {currentTab === 'costing' && <CostingManagement />}
          {currentTab === 'payments' && <PaymentsManagement />}
          {currentTab === 'reports' && <AuditReports />}
          {currentTab === 'benchmark' && <BenchmarkRunner />}
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}

export default App;

