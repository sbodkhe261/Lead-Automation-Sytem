// Global modal handlers to guarantee immediate availability
window.openAlertSettingsModal = function() {
    const m = document.getElementById('settings-modal');
    if (m) {
        m.classList.add('show');
        m.style.display = 'flex';
    }
    if (typeof window.loadNotificationSettings === 'function') {
        window.loadNotificationSettings();
    }
};

window.closeAlertSettingsModal = function() {
    const m = document.getElementById('settings-modal');
    if (m) {
        m.classList.remove('show');
        m.style.display = 'none';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const triggerBtn = document.getElementById('trigger-btn');
    const bulkScrapeBtn = document.getElementById('bulk-scrape-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const leadsGrid = document.getElementById('leads-grid');
    const toast = document.getElementById('toast');
    const searchQueryInput = document.getElementById('search-query');
    const maxResultsInput = document.getElementById('max-results');
    const filterSearchInput = document.getElementById('filter-search');
    const activeTargetDisplay = document.getElementById('active-target-display');
    const pipelineProgressCard = document.getElementById('pipeline-progress-card');
    const progressStatusText = document.getElementById('progress-status-text');
    const progressFill = document.getElementById('progress-fill');
    const exportBtn = document.getElementById('export-btn');
    
    // Stats Ribbon
    const statTotal = document.getElementById('stat-total');
    const statHigh = document.getElementById('stat-high');
    const statMedium = document.getElementById('stat-medium');
    const statAlerted = document.getElementById('stat-alerted');

    // Area Badges
    const badgeAll = document.getElementById('badge-all');
    const badgeChakan = document.getElementById('badge-chakan');
    const badgeBhosari = document.getElementById('badge-bhosari');
    const badgeTalegaon = document.getElementById('badge-talegaon');
    const badgeRanjangaon = document.getElementById('badge-ranjangaon');
    const badgeHadapsar = document.getElementById('badge-hadapsar');
    const badgePimpri = document.getElementById('badge-pimpri');

    // Priority Tab Badges
    const countAll = document.getElementById('count-all');
    const countHigh = document.getElementById('count-high');
    const countMedium = document.getElementById('count-medium');
    const countLow = document.getElementById('count-low');

    // Auto-Pilot Autonomous Mode Elements
    const autopilotDot = document.getElementById('autopilot-dot');
    const autopilotStatusText = document.getElementById('autopilot-status-text');
    const apLastRun = document.getElementById('ap-last-run');
    const apNextRun = document.getElementById('ap-next-run');
    const apLeadsCount = document.getElementById('ap-leads-count');
    const apIntervalSelect = document.getElementById('ap-interval-select');
    const apTriggerNowBtn = document.getElementById('ap-trigger-now-btn');
    const apToggleBtn = document.getElementById('ap-toggle-btn');
    const apToggleText = document.getElementById('ap-toggle-text');

    // 1. Client Outreach Pitch Modal Elements
    const pitchModal = document.getElementById('pitch-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalCompanyName = document.getElementById('modal-company-name');
    const modalLeadMeta = document.getElementById('modal-lead-meta');
    const emailTextBox = document.getElementById('email-text-box');
    const sendPitchTgBtn = document.getElementById('send-pitch-tg-btn');
    const openMailBtn = document.getElementById('open-mail-btn');
    const copyEmailBtn = document.getElementById('copy-email-btn');

    // 2. Internal Lead Intelligence Alert Modal Elements
    const alertModal = document.getElementById('alert-modal');
    const alertModalCloseBtn = document.getElementById('alert-modal-close-btn');
    const alertModalCompanyName = document.getElementById('alert-modal-company-name');
    const alertModalLeadMeta = document.getElementById('alert-modal-lead-meta');
    const alertMetaScore = document.getElementById('alert-meta-score');
    const alertMetaArea = document.getElementById('alert-meta-area');
    const alertMetaPersona = document.getElementById('alert-meta-persona');
    const alertMetaPhone = document.getElementById('alert-meta-phone');
    const alertBriefingBox = document.getElementById('alert-briefing-box');
    const alertSendTgBtn = document.getElementById('alert-send-tg-btn');
    const alertSendEmailBtn = document.getElementById('alert-send-email-btn');
    const alertCopyBtn = document.getElementById('alert-copy-btn');

    // 3. Dispatched Alerts Log Modal Elements
    const cardAlerted = document.getElementById('card-alerted');
    const dispatchedModal = document.getElementById('dispatched-modal');
    const dispatchedModalCloseBtn = document.getElementById('dispatched-modal-close-btn');
    const dispatchedListContainer = document.getElementById('dispatched-list-container');
    const dispatchedCountBadge = document.getElementById('dispatched-count-badge');
    const dispatchedSearchInput = document.getElementById('dispatched-search-input');
    const dispatchedViewGridBtn = document.getElementById('dispatched-view-grid-btn');
    const countAlerted = document.getElementById('count-alerted');

    let allDispatchedLeads = [];

    // Active State
    let currentArea = 'All';
    let currentPriority = 'All';
    let currentActiveLead = null;
    let pollInterval = null;

    // Lighting Theme Switcher & Persistence (Icon-only on far right)
    const themeSelector = document.getElementById('theme-selector');
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeBtnIcon = document.getElementById('theme-btn-icon');
    const themeMenuPopup = document.getElementById('theme-menu-popup');
    
    const themesList = [
        { id: 'lightning', name: 'Lightning', icon: '/ui/icons/theme-lighting.png' },
        { id: 'white', name: 'Clean White', icon: '/ui/icons/theme-white.png' },
        { id: 'warm', name: 'Warm Linen', icon: '/ui/icons/theme-warm.png' },
        { id: 'slate', name: 'Soft Slate', icon: '/ui/icons/theme-slate.png' }
    ];
    let currentTheme = localStorage.getItem('lead_app_theme') || 'lightning';
    
    function applyTheme(theme) {
        currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('lead_app_theme', theme);
        if (themeSelector) {
            themeSelector.value = theme;
        }
        const themeInfo = themesList.find(t => t.id === theme) || themesList[0];
        if (themeBtnIcon) {
            themeBtnIcon.src = themeInfo.icon;
            themeBtnIcon.alt = themeInfo.name;
        }
        if (themeToggleBtn) {
            themeToggleBtn.setAttribute('title', `Lighting Theme: ${themeInfo.name} (Click to switch)`);
        }
        if (themeMenuPopup) {
            themeMenuPopup.querySelectorAll('.theme-option-btn').forEach(btn => {
                if (btn.getAttribute('data-theme') === theme) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }
    }

    applyTheme(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const currentIndex = themesList.findIndex(t => t.id === currentTheme);
            const nextIndex = (currentIndex + 1) % themesList.length;
            const nextTheme = themesList[nextIndex];
            applyTheme(nextTheme.id);
            showToast(`Lighting Theme switched to: ${nextTheme.name}`);
        });
    }

    if (themeMenuPopup) {
        themeMenuPopup.querySelectorAll('.theme-option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const th = btn.getAttribute('data-theme');
                if (th) {
                    applyTheme(th);
                    const info = themesList.find(t => t.id === th);
                    showToast(`Lighting Theme switched to: ${info ? info.name : th}`);
                }
            });
        });
    }

    if (themeSelector) {
        themeSelector.addEventListener('change', (e) => {
            const newTheme = e.target.value;
            applyTheme(newTheme);
            const info = themesList.find(t => t.id === newTheme);
            showToast(`Lighting Theme switched to: ${info ? info.name : newTheme}`);
        });
    }

    // Initial Load
    fetchStats();
    fetchLeads();
    checkPipelineStatus();
    fetchAutoPilotStatus();

    // Poll Auto-Pilot status every 30 seconds
    setInterval(fetchAutoPilotStatus, 30000);

    // Auto-Pilot Toggle Button
    if (apToggleBtn) {
        apToggleBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/autopilot/toggle', { method: 'POST' });
                const data = await res.json();
                renderAutoPilotState(data);
                showToast(data.enabled ? "Auto-Pilot Activated (24/7 Background Sweep Armed)" : "Auto-Pilot Paused");
            } catch (e) {
                showToast("Error toggling auto-pilot");
            }
        });
    }

    // Auto-Pilot Interval Change
    if (apIntervalSelect) {
        apIntervalSelect.addEventListener('change', async () => {
            const val = parseInt(apIntervalSelect.value);
            try {
                const res = await fetch('/api/autopilot/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ interval_hours: val })
                });
                const data = await res.json();
                renderAutoPilotState(data);
                showToast(`Auto-Pilot schedule set to every ${val} hours`);
            } catch (e) {
                showToast("Error updating schedule");
            }
        });
    }

    // Auto-Pilot Trigger Now
    if (apTriggerNowBtn) {
        apTriggerNowBtn.addEventListener('click', async () => {
            apTriggerNowBtn.disabled = true;
            apTriggerNowBtn.innerHTML = '<span>Running Sweep...</span>';
            try {
                const res = await fetch('/api/autopilot/trigger', { method: 'POST' });
                const data = await res.json();
                showToast("Autonomous sweep launched across all industrial zones!");
                setTimeout(() => fetchAutoPilotStatus(), 2000);
            } catch (e) {
                showToast("Error starting sweep");
            } finally {
                setTimeout(() => {
                    apTriggerNowBtn.disabled = false;
                    apTriggerNowBtn.innerHTML = '<span>Run Sweep Now</span>';
                }, 3000);
            }
        });
    }

    async function fetchAutoPilotStatus() {
        try {
            const res = await fetch('/api/autopilot/status');
            const data = await res.json();
            renderAutoPilotState(data);
        } catch (e) {
            console.error("AutoPilot status error:", e);
        }
    }

    function renderAutoPilotState(data) {
        if (!data) return;
        if (apLastRun) apLastRun.textContent = data.last_run || 'Arming initial daily cycle';
        const scheduleLabel = data.interval_hours === 24 ? 'Daily (Every 24 hrs)' : `Every ${data.interval_hours} hrs`;
        if (apNextRun) apNextRun.textContent = data.next_run || scheduleLabel;
        if (apLeadsCount) apLeadsCount.textContent = `${data.leads_found || 0} leads`;

        if (autopilotStatusText) {
            autopilotStatusText.textContent = data.enabled 
                ? (data.is_running_now 
                    ? "Daily Auto-Pilot: Sweeping Pune Hubs for Daily Leads Now..." 
                    : `Daily Auto-Pilot: Active (${scheduleLabel} • Auto-Dispatches High Priority Leads)`)
                : "Daily Auto-Pilot: Paused (Standby)";
        }

        if (autopilotDot) {
            if (data.enabled) {
                autopilotDot.classList.remove('paused');
            } else {
                autopilotDot.classList.add('paused');
            }
        }

        if (apToggleBtn) {
            if (data.enabled) {
                apToggleBtn.classList.add('active');
                apToggleBtn.classList.remove('paused');
                if (apToggleText) apToggleText.textContent = "Auto-Pilot ON";
            } else {
                apToggleBtn.classList.remove('active');
                apToggleBtn.classList.add('paused');
                if (apToggleText) apToggleText.textContent = "Auto-Pilot OFF";
            }
        }

        if (apIntervalSelect && data.interval_hours) {
            apIntervalSelect.value = String(data.interval_hours);
        }
    }

    // AREA TABS NAVIGATION
    document.querySelectorAll('.area-tabs .area-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.area-tabs .area-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentArea = btn.getAttribute('data-area');
            activeTargetDisplay.textContent = currentArea === 'All' ? 'All Pune Hubs' : currentArea;
            
            // Auto update scraper input if selecting a specific area
            if (currentArea !== 'All') {
                searchQueryInput.value = `Manufacturing companies in ${currentArea} Pune`;
            }
            
            updateExportUrl();
            fetchStats();
            fetchLeads();
            showToast(`Filtering by Area: ${currentArea}`);
        });
    });

    // SERVICE PRESET CHIPS NAVIGATION
    document.querySelectorAll('.service-chip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.service-chip-btn').forEach(b => {
                b.classList.remove('active');
                b.style.background = 'rgba(255, 255, 255, 0.05)';
                b.style.color = '#cbd5e1';
                b.style.borderColor = 'rgba(255, 255, 255, 0.12)';
            });
            btn.classList.add('active');
            btn.style.background = 'rgba(56, 189, 248, 0.15)';
            btn.style.color = '#38bdf8';
            btn.style.borderColor = 'rgba(56, 189, 248, 0.35)';

            const service = btn.getAttribute('data-service');
            const areaContext = currentArea === 'All' ? 'Pune MIDC' : currentArea;

            if (service === 'sap') {
                searchQueryInput.value = `SAP ERP manufacturing companies in ${areaContext} Pune`;
            } else if (service === 'powerbi') {
                searchQueryInput.value = `Power BI manufacturing dashboards in ${areaContext} Pune`;
            } else if (service === 'automation') {
                searchQueryInput.value = `Industrial automation and PLC SCADA in ${areaContext} Pune`;
            } else {
                searchQueryInput.value = `Manufacturing companies in ${areaContext} Pune`;
            }
            showToast(`Preset: ${btn.textContent.trim()}`);
        });
    });

    // PRIORITY FILTER TABS
    document.querySelectorAll('.filter-tabs .tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentPriority = btn.getAttribute('data-filter');
            updateExportUrl();
            fetchStats();
            fetchLeads();
        });
    });

    // Real-time keyword filter input
    filterSearchInput.addEventListener('input', () => {
        fetchLeads();
    });

    // Refresh button
    refreshBtn.addEventListener('click', () => {
        refreshBtn.classList.add('spinning');
        Promise.all([fetchStats(), fetchLeads()]).then(() => {
            setTimeout(() => refreshBtn.classList.remove('spinning'), 400);
            showToast("Pipeline refreshed");
        });
    });

    // Clear Filters Button
    const clearFiltersBtnEl = document.getElementById('clear-filters-btn');
    if (clearFiltersBtnEl) {
        clearFiltersBtnEl.addEventListener('click', () => {
            document.querySelectorAll('.area-tabs .area-tab-btn').forEach(b => b.classList.remove('active'));
            const allAreaTab = document.querySelector('.area-tabs .area-tab-btn[data-area="All"]');
            if (allAreaTab) allAreaTab.classList.add('active');
            currentArea = 'All';
            activeTargetDisplay.textContent = 'All Pune Hubs';

            document.querySelectorAll('.filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            const allPrioTab = document.querySelector('.filter-tabs .tab-btn[data-filter="All"]');
            if (allPrioTab) allPrioTab.classList.add('active');
            currentPriority = 'All';

            if (filterSearchInput) filterSearchInput.value = '';

            updateExportUrl();
            fetchStats();
            fetchLeads();
            showToast("Reset all filters to show all leads");
        });
    }

    function updateExportUrl() {
        exportBtn.href = `/api/export?area=${encodeURIComponent(currentArea)}&priority=${encodeURIComponent(currentPriority)}`;
    }

    // Single Area Scraper Trigger
    triggerBtn.addEventListener('click', async () => {
        const query = searchQueryInput.value.trim();
        const maxResults = parseInt(maxResultsInput.value) || 5;

        if (!query) {
            showToast("Please enter a search query.");
            return;
        }

        triggerBtn.disabled = true;
        document.getElementById('btn-loader').style.display = 'block';
        triggerBtn.querySelector('.btn-text').textContent = 'Launching Agent...';

        try {
            const res = await fetch('/api/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    max_results: maxResults,
                    area: currentArea !== 'All' ? currentArea : null
                })
            });

            if (res.ok) {
                showToast("Autonomous Lead Scraper launched in background!");
                startPollingStatus();
            } else {
                const err = await res.json();
                showToast(err.detail || "Scraper failed to start");
            }
        } catch (error) {
            console.error("Scraper launch error:", error);
            showToast("Network error starting scraper pipeline");
        } finally {
            triggerBtn.disabled = false;
            document.getElementById('btn-loader').style.display = 'none';
            triggerBtn.querySelector('.btn-text').textContent = 'Execute AI Scraper';
        }
    });

    // Bulk Scrape All Hubs Trigger
    bulkScrapeBtn.addEventListener('click', async () => {
        if (!confirm("This will scrape and qualify leads across ALL 6 Pune Industrial Hubs (Chakan, Bhosari, Talegaon, Ranjangaon, Hadapsar, Pimpri). Proceed?")) {
            return;
        }

        bulkScrapeBtn.disabled = true;
        bulkScrapeBtn.textContent = 'Harvesting...';

        try {
            const res = await fetch('/api/scrape/bulk', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ results_per_area: 4 })
            });

            if (res.ok) {
                showToast("Bulk multi-area harvest initiated across all Pune hubs!");
                startPollingStatus();
            } else {
                const err = await res.json();
                showToast(err.detail || "Bulk scrape failed to start");
            }
        } catch (e) {
            showToast("Network error initiating bulk scrape");
        } finally {
            bulkScrapeBtn.disabled = false;
            bulkScrapeBtn.textContent = 'Bulk Harvest All Hubs';
        }
    });

    // Polling Pipeline Status
    function startPollingStatus() {
        pipelineProgressCard.classList.add('active');
        if (pollInterval) clearInterval(pollInterval);
        
        pollInterval = setInterval(async () => {
            await checkPipelineStatus();
        }, 1800);
    }

    async function checkPipelineStatus() {
        try {
            const res = await fetch('/api/status');
            const status = await res.json();

            if (status.is_running) {
                pipelineProgressCard.classList.add('active');
                progressStatusText.textContent = `${status.current_step} (${status.leads_processed}/${status.total_target})`;
                const pct = status.total_target > 0 
                    ? Math.max(12, Math.min(100, (status.leads_processed / status.total_target) * 100))
                    : 30;
                progressFill.style.width = `${pct}%`;
            } else {
                if (pipelineProgressCard.classList.contains('active')) {
                    progressFill.style.width = '100%';
                    progressStatusText.textContent = "Pipeline completed. Leads scored & stored!";
                    setTimeout(() => {
                        pipelineProgressCard.classList.remove('active');
                    }, 3500);
                    fetchStats();
                    fetchLeads();
                }
                if (pollInterval) {
                    clearInterval(pollInterval);
                    pollInterval = null;
                }
            }
        } catch (e) {
            console.error("Status check error:", e);
        }
    }

    // Stats Fetch & Area Badges Update (Dynamically scoped to selected filters)
    async function fetchStats() {
        try {
            const areaParam = encodeURIComponent(currentArea || 'All');
            const prioParam = encodeURIComponent(currentPriority || 'All');
            const res = await fetch(`/api/stats?area=${areaParam}&priority=${prioParam}`);
            const data = await res.json();
            
            // Top Ribbon: Total overall in Database
            statTotal.textContent = data.total_leads || 0;
            statHigh.textContent = data.high_priority || 0;
            statMedium.textContent = data.medium_priority || 0;
            statAlerted.textContent = data.alerts_dispatched || 0;

            // Priority Tab Badges: Dynamically show exact count for currently selected area!
            const scoped = data.area_scoped || {};
            if (countAll) countAll.textContent = scoped.total !== undefined ? scoped.total : (data.total_leads || 0);
            if (countHigh) countHigh.textContent = scoped.high !== undefined ? scoped.high : (data.high_priority || 0);
            if (countMedium) countMedium.textContent = scoped.medium !== undefined ? scoped.medium : (data.medium_priority || 0);
            if (countLow) countLow.textContent = scoped.low !== undefined ? scoped.low : (data.low_priority || 0);
            if (countAlerted) countAlerted.textContent = scoped.alerted !== undefined ? scoped.alerted : (data.alerts_dispatched || 0);

            // Area Badges: Dynamically show exact count for currently selected priority!
            const ac = data.area_counts || {};
            badgeAll.textContent = currentPriority !== 'All' ? (scoped.total || 0) : (data.total_leads || 0);
            badgeChakan.textContent = ac['Chakan MIDC'] || 0;
            badgeBhosari.textContent = ac['Bhosari MIDC'] || 0;
            badgeTalegaon.textContent = ac['Talegaon MIDC'] || 0;
            badgeRanjangaon.textContent = ac['Ranjangaon MIDC'] || 0;
            badgeHadapsar.textContent = ac['Hadapsar'] || 0;
            badgePimpri.textContent = ac['Pimpri-Chinchwad'] || 0;
        } catch (e) {
            console.error("Stats fetch error:", e);
        }
    }

    // Leads Fetch by Area & Priority
    async function fetchLeads() {
        const searchTerm = filterSearchInput.value.trim();
        let url = currentPriority === 'Alerted'
            ? `/api/leads?alerted_only=true`
            : `/api/leads?priority=${encodeURIComponent(currentPriority)}`;

        if (currentArea && currentArea !== 'All') {
            url += `&area=${encodeURIComponent(currentArea)}`;
        }
        if (searchTerm) {
            url += `&search=${encodeURIComponent(searchTerm)}`;
        }

        try {
            const res = await fetch(url);
            const leads = await res.json();
            renderLeads(leads);
        } catch (error) {
            console.error("Leads fetch error:", error);
            leadsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 3rem;">
                Failed to load leads from intelligence database.
            </div>`;
        }
    }

    // Render Leads Cards
    function renderLeads(leads) {
        // Update live status & result count bar
        const activeResultCount = document.getElementById('active-result-count');
        const activeAreaName = document.getElementById('active-area-name');
        const activePrioText = document.getElementById('active-prio-text');
        const clearFiltersBtn = document.getElementById('clear-filters-btn');

        if (activeResultCount) activeResultCount.textContent = leads ? leads.length : 0;
        if (activeAreaName) activeAreaName.textContent = currentArea === 'All' ? 'All Areas' : currentArea;
        if (activePrioText) {
            if (currentPriority !== 'All') {
                activePrioText.textContent = ` • ${currentPriority} Priority`;
            } else {
                activePrioText.textContent = '';
            }
        }
        if (clearFiltersBtn) {
            if (currentArea !== 'All' || currentPriority !== 'All' || (filterSearchInput && filterSearchInput.value.trim())) {
                clearFiltersBtn.style.display = 'inline-block';
            } else {
                clearFiltersBtn.style.display = 'none';
            }
        }

        if (!leads || leads.length === 0) {
            const areaLabel = currentArea === 'All' ? 'all Pune industrial hubs' : currentArea;
            const priorityLabel = currentPriority === 'Alerted' 
                ? 'Dispatched Alert' 
                : (currentPriority === 'All' ? '' : `${currentPriority} Priority`);
            
            leadsGrid.innerHTML = `
                <div class="empty-area-cta">
                    <img src="/ui/icons/factory.png" alt="Industrial Plants" style="width: 54px; height: 54px; object-fit: contain; margin-bottom: 0.6rem;">
                    <h3 class="empty-cta-title">No ${priorityLabel} leads found in ${areaLabel}</h3>
                    <p class="empty-cta-desc">
                        ${currentArea !== 'All' 
                            ? `You can auto-discover and harvest manufacturing leads specifically in ${currentArea} right now.`
                            : `Try switching area tabs or trigger the AI scraper to collect leads.`}
                    </p>
                    ${currentArea !== 'All' ? `
                        <button class="btn btn-primary" id="auto-scrape-area-btn">
                            <span><img src="/ui/icons/bolt.png" alt="Discover" class="ui-icon-btn"> Discover & Scrape Leads in ${currentArea}</span>
                        </button>
                    ` : `
                        <button class="btn btn-primary" id="auto-scrape-all-btn">
                            <span><img src="/ui/icons/rocket.png" alt="Bulk Harvest" class="ui-icon-btn"> Bulk Harvest All Pune Hubs</span>
                        </button>
                    `}
                    <div style="display:flex; gap:0.75rem; flex-wrap:wrap; justify-content:center; margin-top:0.5rem;">
                        ${currentPriority !== 'All' ? `
                            <button class="btn btn-secondary btn-sm" id="reset-priority-btn">
                                <span>Show All Priorities in ${areaLabel}</span>
                            </button>
                        ` : ''}
                        ${currentArea !== 'All' ? `
                            <button class="btn btn-secondary btn-sm" id="reset-area-btn">
                                <span>Show All Pune Hubs</span>
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;

            // Attach Empty State Actions
            const resetPriorityBtn = document.getElementById('reset-priority-btn');
            if (resetPriorityBtn) {
                resetPriorityBtn.addEventListener('click', () => {
                    document.querySelectorAll('.filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                    const allTab = document.querySelector('.filter-tabs .tab-btn[data-filter="All"]');
                    if (allTab) allTab.classList.add('active');
                    currentPriority = 'All';
                    fetchLeads();
                });
            }

            const resetAreaBtn = document.getElementById('reset-area-btn');
            if (resetAreaBtn) {
                resetAreaBtn.addEventListener('click', () => {
                    document.querySelectorAll('.area-tabs .area-tab-btn').forEach(b => b.classList.remove('active'));
                    const allAreaTab = document.querySelector('.area-tabs .area-tab-btn[data-area="All"]');
                    if (allAreaTab) allAreaTab.classList.add('active');
                    currentArea = 'All';
                    activeTargetDisplay.textContent = 'All Pune Hubs';
                    fetchLeads();
                });
            }

            const autoAreaBtn = document.getElementById('auto-scrape-area-btn');
            if (autoAreaBtn) {
                autoAreaBtn.addEventListener('click', () => {
                    searchQueryInput.value = `Manufacturing companies in ${currentArea} Pune`;
                    triggerBtn.click();
                });
            }

            const autoAllBtn = document.getElementById('auto-scrape-all-btn');
            if (autoAllBtn) {
                autoAllBtn.addEventListener('click', () => {
                    bulkScrapeBtn.click();
                });
            }

            return;
        }

        leadsGrid.innerHTML = leads.map(lead => {
            // Tech stack badges
            let techPillsHtml = '';
            if (lead.tech_stack && lead.tech_stack.length > 0) {
                techPillsHtml = lead.tech_stack.map(tech => {
                    const isKey = ['SAP', 'Power BI', 'PowerBI', 'Automation', 'SCADA', 'PLC', 'MES', 'Siemens', 'Rockwell', 'Robotics'].some(k => tech.toLowerCase().includes(k.toLowerCase()));
                    return `<span class="tech-pill ${isKey ? 'highlight' : ''}">${escapeHtml(tech)}</span>`;
                }).join('');
            } else {
                techPillsHtml = '<span class="tech-pill">Industrial Manufacturing</span>';
            }

            // Key primary capability highlight for front card
            let primaryFocus = 'Manufacturing & Industrial Automation';
            if (lead.tech_stack && lead.tech_stack.length > 0) {
                const keyTech = lead.tech_stack.find(tech => ['SAP', 'Power BI', 'Automation', 'SCADA', 'PLC', 'MES', 'Siemens', 'Robotics'].some(k => tech.toLowerCase().includes(k.toLowerCase())));
                if (keyTech) {
                    primaryFocus = keyTech;
                } else {
                    primaryFocus = lead.tech_stack[0];
                }
            }

            // Alerts status badge
            const alertBadge = lead.alert_sent
                ? `<span class="alert-status-badge"><span><img src="/ui/icons/check.png" alt="Delivered" class="ui-icon-badge"></span> Alert Dispatched</span>`
                : `<span class="alert-status-badge pending"><span>○</span> Pending Outreach</span>`;

            // Score breakdown hints
            const b = lead.score_breakdown || {};
            const breakdownTooltip = `SAP Fit: +${b.sap_fit ?? b.power_bi_sap ?? 0} | Power BI: +${b.power_bi_fit ?? 0} | Automation: +${b.industrial_automation_fit ?? b.industrial_software ?? 0} | Pune Corridor: +${b.location_fit ?? b.pune_midc ?? 0}`;

            const phoneSnippet = lead.phone ? `<a href="tel:${escapeHtml(lead.phone)}" style="color:var(--accent-blue); font-family:var(--font-mono); font-weight:600; text-decoration:none;">${escapeHtml(lead.phone)}</a>` : '<span style="color:var(--text-dim);">Phone on Maps</span>';
            const displayArea = lead.area || 'Pune MIDC';

            // Drip Campaign Status Badge
            const currentStep = lead.campaign_step || 0;
            const dripLabel = currentStep === 0 ? 'Drip: Step 0/3 (New)' : (currentStep >= 3 ? 'Drip: 3/3 (Done)' : `Drip: Step ${currentStep}/3`);
            const dripColor = currentStep > 0 ? 'var(--priority-high)' : 'var(--text-dim)';

            const targetPersona = lead.decision_maker_name || lead.decision_maker || 'Head of IT / Plant Operations';

            return `
                <div class="lead-card priority-${lead.priority}" id="lead-${lead.id}" data-id="${lead.id}" title="Click card to open full intelligence detail card">
                    <!-- Top Section: Area & Score -->
                    <div class="card-top">
                        <div class="card-title-group">
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 4px;">
                                <span class="card-area-pill">
                                    <img src="/ui/icons/location.png" alt="" class="ui-icon-badge">
                                    <span>${escapeHtml(displayArea)}</span>
                                </span>
                                <div class="card-score-pill" title="${breakdownTooltip}">
                                    <span>${lead.score}</span><span style="font-size: 0.74rem; opacity: 0.8;">/100</span>
                                </div>
                            </div>
                            <h3 class="card-company-name">${escapeHtml(lead.company_name)}</h3>
                            <div class="card-meta-links">
                                <span class="meta-rating"><img src="/ui/icons/star.png" alt="Rating" class="ui-icon-badge"> ${lead.google_rating ? lead.google_rating.toFixed(1) : '4.5'}</span>
                                <span>•</span>
                                ${lead.website ? `<a href="${lead.website}" target="_blank" class="meta-link" title="Visit company website">Website &nearr;</a>` : '<span style="color:var(--text-dim);">No Website</span>'}
                                <span>•</span>
                                <span style="color:var(--text-dim); text-transform: capitalize;">${escapeHtml(lead.source || 'MIDC Hub')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Key Spec Details -->
                    <div class="card-front-details">
                        <div class="info-row">
                            <span class="info-label">Contact:</span>
                            <span class="info-value">${phoneSnippet}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Core Focus:</span>
                            <span class="info-value" style="font-weight: 600; color: var(--accent-blue);">${escapeHtml(primaryFocus)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Target Persona:</span>
                            <span class="info-value" style="color: var(--text-muted); font-size: 0.84rem;">${escapeHtml(targetPersona)}</span>
                        </div>
                        <div class="card-badges-row">
                            ${alertBadge}
                            <button class="drip-badge-btn" data-id="${lead.id}" title="Manage Automated Drip Outreach Sequence (Day 1 / Day 3 / Day 7)" style="background: #ffffff; border: 1px solid var(--border-subtle); border-radius: var(--radius-xs); padding: 2px 8px; font-size: 0.78rem; color: ${dripColor}; font-weight: 500; cursor: pointer;">
                                ${dripLabel}
                            </button>
                        </div>
                    </div>

                    <!-- Tech Stack Highlights -->
                    <div class="tech-tag-container">
                        ${techPillsHtml}
                    </div>

                    <!-- Card Actions Footer -->
                    <div class="card-footer">
                        <div style="font-size: 0.78rem; color: var(--text-dim); font-weight: 500; font-family: var(--font-mono);">
                            <span>#${lead.id}</span>
                        </div>
                        <div class="card-btn-group">
                            <button class="btn btn-secondary btn-sm enrich-single-btn" data-id="${lead.id}" title="Enrich Decision Makers, LinkedIn, MCA & Technographics">
                                <span>Enrich</span>
                            </button>
                            <button class="btn btn-secondary btn-sm view-pitch-btn" data-id="${lead.id}" title="Open Tailored B2B Proposal to Send to Client">
                                <span>Pitch</span>
                            </button>
                            <button class="btn btn-secondary btn-sm notify-team-btn" data-id="${lead.id}" title="Open Lead Intelligence Briefing & Mobile Alerts">
                                <span>Alert</span>
                            </button>
                            <button class="btn btn-secondary btn-sm rescore-btn" data-id="${lead.id}" title="Re-evaluate with Gemini">
                                <span>Rescore</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        attachCardEventHandlers(leads);
    }

    // Attach Event Handlers to Rendered Cards
    function attachCardEventHandlers(leads) {
        // Clicking specific lead card immediately opens additional details on inner detail card modal
        document.querySelectorAll('.lead-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('button') || e.target.closest('a') || e.target.closest('input')) {
                    return;
                }
                const leadId = parseInt(card.getAttribute('data-id'));
                const lead = leads.find(l => l.id === leadId);
                if (lead) {
                    openLeadDetailModal(lead);
                }
            });
        });

        // 1. Open Pitch Modal (Client-facing Outreach Pitch)
        document.querySelectorAll('.view-pitch-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const leadId = parseInt(btn.getAttribute('data-id'));
                const lead = leads.find(l => l.id === leadId);
                if (lead) {
                    openPitchModal(lead);
                }
            });
        });

        // 2. Open Alert Modal (Internal Lead Intelligence Briefing for Team/Mobile)
        document.querySelectorAll('.notify-team-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const leadId = parseInt(btn.getAttribute('data-id'));
                const lead = leads.find(l => l.id === leadId);
                if (lead) {
                    openAlertModal(lead);
                }
            });
        });

        // 3. Open Drip Campaign Sequence Modal
        document.querySelectorAll('.drip-badge-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const leadId = parseInt(btn.getAttribute('data-id'));
                openDripModal(leadId);
            });
        });

        // 4. 1-Click Enrich Single Lead
        document.querySelectorAll('.enrich-single-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const leadId = btn.getAttribute('data-id');
                btn.textContent = "Enriching...";
                try {
                    const res = await fetch(`/api/leads/${leadId}/enrich`, { method: 'POST' });
                    if (res.ok) {
                        showToast("Lead enriched with Decision Maker, LinkedIn, MCA & Technographics!");
                        fetchLeads();
                    } else {
                        showToast("Enrichment failed");
                    }
                } catch (err) {
                    showToast("Error enriching lead");
                } finally {
                    btn.textContent = "Enrich";
                }
            });
        });

        // 5. Re-score Lead
        document.querySelectorAll('.rescore-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const leadId = btn.getAttribute('data-id');
                btn.classList.add('spinning');
                try {
                    const res = await fetch(`/api/leads/${leadId}/rescore`, { method: 'POST' });
                    if (res.ok) {
                        showToast("Lead re-evaluated by Gemini Agent!");
                        fetchStats();
                        fetchLeads();
                    }
                } catch (err) {
                    showToast("Failed to re-score lead");
                } finally {
                    btn.classList.remove('spinning');
                }
            });
        });
    }

    // ==========================================
    // 0. DEDICATED LEAD DETAIL CARD MODAL
    // ==========================================
    const detailModal = document.getElementById('lead-detail-modal');
    const detailCardCloseBtn = document.getElementById('detail-card-close-btn');

    function openLeadDetailModal(lead) {
        currentActiveLead = lead;
        if (!detailModal) return;

        const areaEl = document.getElementById('detail-card-area');
        const scoreEl = document.getElementById('detail-card-score');
        const nameEl = document.getElementById('detail-card-company-name');
        const metaLinksEl = document.getElementById('detail-card-meta-links');
        const bodyEl = document.getElementById('detail-card-body');
        const idTagEl = document.getElementById('detail-card-id-tag');
        const actionsEl = document.getElementById('detail-card-actions');

        const displayArea = lead.area || 'Pune MIDC';
        const b = lead.score_breakdown || {};
        const breakdownTooltip = `SAP Fit: +${b.sap_fit ?? b.power_bi_sap ?? 0} | Power BI: +${b.power_bi_fit ?? 0} | Automation: +${b.industrial_automation_fit ?? b.industrial_software ?? 0} | Pune Corridor: +${b.location_fit ?? b.pune_midc ?? 0}`;

        if (areaEl) areaEl.innerHTML = `<img src="/ui/icons/location.png" alt="Area" class="ui-icon-badge"> ${escapeHtml(displayArea)}`;
        if (scoreEl) {
            scoreEl.innerHTML = `<img src="/ui/icons/star.png" alt="Score" class="ui-icon-badge"> ${lead.score}/100 • ${escapeHtml(lead.priority || 'Normal')} Priority`;
            scoreEl.title = breakdownTooltip;
        }
        if (nameEl) nameEl.textContent = lead.company_name;

        if (metaLinksEl) {
            metaLinksEl.innerHTML = `
                <span class="meta-rating"><img src="/ui/icons/star.png" alt="Rating" class="ui-icon-badge"> ${lead.google_rating ? lead.google_rating.toFixed(1) : '4.5'}</span>
                <span>•</span>
                ${lead.website ? `<a href="${lead.website}" target="_blank" class="meta-link" title="Visit website">Website &nearr;</a>` : '<span style="color:var(--text-dim);">No Website</span>'}
                <span>•</span>
                <span style="color:var(--text-dim);">${escapeHtml(lead.source || 'google_maps')}</span>
                <span>•</span>
                <span style="color:var(--text-dim);">Lead #${lead.id}</span>
            `;
        }

        if (idTagEl) idTagEl.textContent = `Lead ID #${lead.id} • ${displayArea}`;

        // Tech Stack pills
        let techPillsHtml = '';
        if (lead.tech_stack && lead.tech_stack.length > 0) {
            techPillsHtml = lead.tech_stack.map(tech => {
                const isKey = ['SAP', 'Power BI', 'PowerBI', 'Automation', 'SCADA', 'PLC', 'MES', 'Siemens', 'Rockwell', 'Robotics'].some(k => tech.toLowerCase().includes(k.toLowerCase()));
                return `<span class="tech-pill ${isKey ? 'highlight' : ''}">${escapeHtml(tech)}</span>`;
            }).join('');
        } else {
            techPillsHtml = '<span class="tech-pill">Industrial Manufacturing</span>';
        }

        // Hiring signals
        let hiringHtml = '';
        if (lead.hiring_signals && lead.hiring_signals.length > 0) {
            const job = lead.hiring_signals[0];
            const jobTitle = typeof job === 'object' ? (job.title || 'Enterprise Role') : String(job);
            hiringHtml = `
                <div style="background: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.25); border-radius: 6px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: #d97706;">ACTIVE HIRING INTENT:</span>
                    <span style="font-size: 0.88rem; color: var(--text-main); font-weight: 600;">${escapeHtml(jobTitle)}</span>
                </div>
            `;
        }

        // Decision Maker
        const dmName = lead.decision_maker_name;
        const dmEmail = lead.decision_maker_email;
        const dmLi = lead.decision_maker_linkedin;
        let dmHtml = '';
        if (dmName || dmEmail || dmLi) {
            dmHtml = `
                <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 16px;">
                    <div style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">Verified Decision Maker</div>
                    <div style="font-size: 1rem; font-weight: 700; color: var(--text-main);">${escapeHtml(dmName || lead.decision_maker || 'Plant Operations Head')}</div>
                    <div style="display: flex; gap: 14px; align-items: center; margin-top: 6px; flex-wrap: wrap;">
                        ${dmEmail ? `<a href="mailto:${escapeHtml(dmEmail)}" style="font-family: var(--font-mono); font-size: 0.86rem; color: var(--accent-blue); text-decoration: none;"><img src="/ui/icons/mail.png" alt="Email" class="ui-icon-badge"> ${escapeHtml(dmEmail)}</a>` : ''}
                        ${dmLi ? `<a href="${dmLi}" target="_blank" style="font-size: 0.84rem; color: var(--accent-cyan); text-decoration: underline; font-weight: 600;">LinkedIn Profile &nearr;</a>` : ''}
                    </div>
                </div>
            `;
        } else {
            dmHtml = `
                <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 16px;">
                    <div style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">Target Persona</div>
                    <div style="font-size: 0.96rem; font-weight: 600; color: var(--accent-blue);">${escapeHtml(lead.decision_maker || 'Head of IT / Plant Operations')}</div>
                </div>
            `;
        }

        // MCA Financials
        let mcaHtml = '';
        if (lead.cin || lead.revenue_range || lead.automation_budget) {
            mcaHtml = `
                <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 16px;">
                    <div style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 6px;">Corporate MCA Intelligence & Budget</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">
                        ${lead.cin ? `<div><span style="font-size: 0.8rem; color: var(--text-dim);">CIN: </span><span style="font-family: var(--font-mono); font-size: 0.85rem; font-weight: 600;">${escapeHtml(lead.cin)}</span></div>` : ''}
                        ${lead.revenue_range ? `<div><span style="font-size: 0.8rem; color: var(--text-dim);">Revenue: </span><span style="font-size: 0.88rem; font-weight: 700; color: var(--priority-high);">${escapeHtml(lead.revenue_range)}</span></div>` : ''}
                    </div>
                    ${lead.automation_budget ? `
                        <div style="margin-top: 8px; padding: 6px 10px; background: rgba(5, 150, 105, 0.08); border: 1px dashed rgba(5, 150, 105, 0.3); border-radius: 4px;">
                            <span style="font-size: 0.8rem; color: var(--priority-high); font-weight: 700;">Est. Automation & IT Budget:</span>
                            <span style="font-size: 0.88rem; font-weight: 700; color: var(--text-main); margin-left: 4px;">${escapeHtml(lead.automation_budget)}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // Technographics
        let techSignalsHtml = '';
        const tg = lead.technographics || {};
        const activeSubs = tg.active_subdomains || [];
        const isM365 = tg.microsoft_365;
        if (activeSubs.length > 0 || isM365) {
            techSignalsHtml = `
                <div>
                    <div style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 6px;">Detected Digital Infrastructure & Subdomains</div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        ${activeSubs.map(sub => `<span style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.25); color: #0284c7; border-radius: 4px; padding: 3px 8px; font-size: 0.78rem; font-family: var(--font-mono); font-weight:600;">${escapeHtml(sub)}</span>`).join('')}
                        ${isM365 ? `<span style="background: rgba(5, 150, 105, 0.08); border: 1px solid rgba(5, 150, 105, 0.25); color: #059669; border-radius: 4px; padding: 3px 8px; font-size: 0.78rem; font-weight:600;">Microsoft 365 Cloud</span>` : ''}
                    </div>
                </div>
            `;
        }

        const phoneSnippet = lead.phone ? `<a href="tel:${escapeHtml(lead.phone)}" style="color:var(--accent-blue); font-family:var(--font-mono); font-weight:600; text-decoration:none;">${escapeHtml(lead.phone)}</a>` : '<span style="color:var(--text-dim);">Phone on Maps</span>';
        const currentStep = lead.campaign_step || 0;
        const dripLabel = currentStep === 0 ? 'Drip: Step 0/3 (New)' : (currentStep >= 3 ? 'Drip: 3/3 (Completed)' : `Drip: Step ${currentStep}/3`);

        if (bodyEl) {
            bodyEl.innerHTML = `
                <!-- Snapshot Meta Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.65rem;">
                    <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.7rem 0.9rem;">
                        <div style="font-size: 0.76rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em;">Direct Phone</div>
                        <div style="font-size: 0.92rem; font-weight: 700; margin-top: 3px;">${phoneSnippet}</div>
                    </div>
                    <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.7rem 0.9rem;">
                        <div style="font-size: 0.76rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em;">Industrial Area</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: var(--text-main); margin-top: 3px;">${escapeHtml(displayArea)}</div>
                    </div>
                    <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.7rem 0.9rem;">
                        <div style="font-size: 0.76rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em;">Score & Priority</div>
                        <div style="font-size: 0.92rem; font-weight: 800; color: var(--accent-blue); margin-top: 3px;">${lead.score}/100 (${lead.priority || 'Normal'})</div>
                    </div>
                    <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.7rem 0.9rem;">
                        <div style="font-size: 0.76rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em;">Drip Status</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: var(--priority-high); margin-top: 3px;">${escapeHtml(dripLabel)}</div>
                    </div>
                </div>

                ${hiringHtml}

                <!-- Address -->
                <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 16px;">
                    <div style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">Plant Location / Registered Address</div>
                    <div style="font-size: 0.92rem; color: var(--text-main); line-height: 1.45;">${escapeHtml(lead.address || displayArea)}</div>
                </div>

                ${dmHtml}

                ${mcaHtml}

                ${techSignalsHtml}

                <!-- Tech Stack -->
                <div>
                    <div style="font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 6px;">Identified Technologies & Systems</div>
                    <div class="tech-tag-container">
                        ${techPillsHtml}
                    </div>
                </div>

                <!-- Signals / Score Reasoning -->
                ${lead.score_reasoning ? `
                    <div class="reasoning-box" style="margin-top: 0;">
                        <strong>AI Qualification Signals & Strategic Fit:</strong><br>
                        ${escapeHtml(lead.score_reasoning)}
                    </div>
                ` : ''}
            `;
        }

        if (actionsEl) {
            actionsEl.innerHTML = `
                <button class="btn btn-secondary btn-sm" id="detail-card-enrich-btn" title="Enrich Decision Makers, LinkedIn & MCA">
                    <span>Enrich Intel</span>
                </button>
                <button class="btn btn-secondary btn-sm" id="detail-card-pitch-btn" title="Open Tailored B2B Proposal">
                    <span>Pitch Proposal</span>
                </button>
                <button class="btn btn-secondary btn-sm" id="detail-card-alert-btn" title="Open Alert Briefing">
                    <span>Send Alert</span>
                </button>
                <button class="btn btn-secondary btn-sm" id="detail-card-drip-btn" title="Open Drip Campaign Sequence">
                    <span>Drip Sequence</span>
                </button>
                <button class="btn btn-secondary btn-sm" id="detail-card-close-btn2">
                    <span>Close</span>
                </button>
            `;

            const enrichBtn = document.getElementById('detail-card-enrich-btn');
            if (enrichBtn) {
                enrichBtn.addEventListener('click', async () => {
                    enrichBtn.textContent = "Enriching...";
                    try {
                        const res = await fetch(`/api/leads/${lead.id}/enrich`, { method: 'POST' });
                        if (res.ok) {
                            showToast("Lead enriched successfully!");
                            closeLeadDetailModal();
                            fetchLeads();
                        } else {
                            showToast("Enrichment failed");
                        }
                    } catch (e) {
                        showToast("Error enriching lead");
                    } finally {
                        enrichBtn.textContent = "Enrich Intel";
                    }
                });
            }

            const pitchBtn = document.getElementById('detail-card-pitch-btn');
            if (pitchBtn) {
                pitchBtn.addEventListener('click', () => {
                    closeLeadDetailModal();
                    openPitchModal(lead);
                });
            }

            const alertBtn = document.getElementById('detail-card-alert-btn');
            if (alertBtn) {
                alertBtn.addEventListener('click', () => {
                    closeLeadDetailModal();
                    openAlertModal(lead);
                });
            }

            const dripBtn = document.getElementById('detail-card-drip-btn');
            if (dripBtn) {
                dripBtn.addEventListener('click', () => {
                    closeLeadDetailModal();
                    openDripModal(lead.id);
                });
            }

            const closeBtn2 = document.getElementById('detail-card-close-btn2');
            if (closeBtn2) {
                closeBtn2.addEventListener('click', closeLeadDetailModal);
            }
        }

        if (detailModal) {
            detailModal.classList.add('show');
            detailModal.style.display = 'flex';
        }
    }

    function closeLeadDetailModal() {
        if (detailModal) {
            detailModal.classList.remove('show');
            detailModal.style.display = 'none';
        }
    }

    if (detailCardCloseBtn) {
        detailCardCloseBtn.addEventListener('click', closeLeadDetailModal);
    }

    if (detailModal) {
        detailModal.addEventListener('click', (e) => {
            if (e.target === detailModal) closeLeadDetailModal();
        });
    }

    // ==========================================
    // 1. CLIENT OUTREACH PITCH MODAL
    // ==========================================
    function openPitchModal(lead) {
        currentActiveLead = lead;
        if (modalCompanyName) modalCompanyName.innerHTML = `<img src="/ui/icons/chat.png" alt="Pitch" class="ui-icon-modal-title"> ${escapeHtml(lead.company_name)}`;
        if (modalLeadMeta) modalLeadMeta.textContent = `Target: ${lead.decision_maker || 'Plant Operations / IT Head'} • Area: ${lead.area || 'Pune MIDC'} • Score: ${lead.score}/100`;

        let pitchText = lead.pitch || lead.generated_pitch || '';
        if (!pitchText) {
            pitchText = `Subject: Power BI & Industrial Automation Solutions for ${lead.company_name}\n\nHi Team at ${lead.company_name},\n\nI noticed ${lead.company_name} is operating a major manufacturing setup in ${lead.area || 'Pune'}. At BrownBox Innovation, we specialize in helping industrial manufacturing facilities eliminate manual data extraction and build real-time visibility.\n\nOur Specialized Services for Your Plant:\n• Live Executive Power BI Dashboards: Real-time OEE, Machine Downtime, Yield & Scrap tracking.\n• Direct SAP / ERP Integration: Seamless data pipelines that eliminate daily Excel extraction work.\n• Custom Shop-floor Telemetry & MES: Bridging machine PLC/SCADA signals with management analytics.\n\nWould you be open for a brief 10-minute discovery call this Thursday to explore how we can support your operations?\n\nBest regards,\nBrownBox Innovation Team\nPune, Maharashtra | +91 91234 56789`;
        }

        if (emailTextBox) {
            emailTextBox.value = pitchText;
        }

        if (pitchModal) pitchModal.classList.add('show');
    }

    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', () => {
            if (pitchModal) pitchModal.classList.remove('show');
        });
    }

    if (pitchModal) {
        pitchModal.addEventListener('click', (e) => {
            if (e.target === pitchModal) {
                pitchModal.classList.remove('show');
            }
        });
    }

    // Send Client Pitch copy to user's Telegram
    if (sendPitchTgBtn) {
        sendPitchTgBtn.addEventListener('click', async () => {
            if (!currentActiveLead) return;
            const orig = sendPitchTgBtn.innerHTML;
            sendPitchTgBtn.innerHTML = '<span><img src="/ui/icons/clock.png" alt="Sending" class="ui-icon-btn"> Sending...</span>';
            showToast("Sending pitch copy directly to your Telegram...");
            try {
                const pitchContent = emailTextBox ? emailTextBox.value : '';
                const tgMsg = `<b>[CLIENT PITCH — ${escapeHtml(currentActiveLead.company_name)}]</b>\n\n` +
                              `<b>Area:</b> ${currentActiveLead.area || 'Pune'}\n` +
                              `<b>Target Persona:</b> ${currentActiveLead.decision_maker || 'Plant Head'}\n` +
                              `<b>Phone:</b> ${currentActiveLead.phone || 'N/A'}\n\n` +
                              `<b>Client Pitch Text:</b>\n${pitchContent}`;

                const res = await fetch(`/api/leads/${currentActiveLead.id}/send-alert`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ channel: 'telegram', custom_message: tgMsg })
                });
                const data = await res.json();
                const tgRes = data.results && data.results.telegram ? data.results.telegram : null;

                if (tgRes && tgRes.success) {
                    sendPitchTgBtn.innerHTML = '<span><img src="/ui/icons/check.png" alt="Sent" class="ui-icon-btn"> Sent to Telegram!</span>';
                    showToast("Client pitch delivered to your Telegram (@BBI_leads_alert_bot)!");
                    setTimeout(() => { sendPitchTgBtn.innerHTML = orig; }, 2500);
                } else {
                    sendPitchTgBtn.innerHTML = orig;
                    const err = tgRes && tgRes.error ? tgRes.error : "Failed to send Telegram message";
                    showToast("Telegram: " + err);
                }
            } catch (err) {
                sendPitchTgBtn.innerHTML = orig;
                showToast("Failed to connect to Telegram service");
            }
        });
    }

    // Open Pitch in Default Mail Client (mailto:)
    if (openMailBtn) {
        openMailBtn.addEventListener('click', () => {
            if (!currentActiveLead) return;
            const subject = encodeURIComponent(`Power BI & Industrial Automation Solutions for ${currentActiveLead.company_name}`);
            const body = encodeURIComponent(emailTextBox.value);
            window.location.href = `mailto:?subject=${subject}&body=${body}`;
            showToast("Opening mail client to send pitch to client...");
        });
    }

    // Copy Client Pitch to Clipboard
    if (copyEmailBtn) {
        copyEmailBtn.addEventListener('click', () => {
            if (emailTextBox) {
                navigator.clipboard.writeText(emailTextBox.value);
                showToast("Pitch copied to clipboard!");
            }
        });
    }

    // ==========================================
    // 2. INTERNAL LEAD INTELLIGENCE ALERT MODAL
    // ==========================================
    function openAlertModal(lead) {
        currentActiveLead = lead;
        if (alertModalCompanyName) alertModalCompanyName.innerHTML = `<img src="/ui/icons/bell.png" alt="Alert" class="ui-icon-modal-title"> ${escapeHtml(lead.company_name)}`;
        if (alertModalLeadMeta) alertModalLeadMeta.textContent = `Score: ${lead.score}/100 • Priority: ${lead.priority || 'High'} • Target: ${lead.decision_maker || 'Plant Operations'}`;

        if (alertMetaScore) alertMetaScore.textContent = `${lead.score}/100 (${lead.priority || 'High'})`;
        if (alertMetaArea) alertMetaArea.textContent = lead.area || 'Pune MIDC';
        if (alertMetaPersona) alertMetaPersona.textContent = lead.decision_maker || 'Head of IT / Plant';
        if (alertMetaPhone) alertMetaPhone.textContent = lead.phone || 'Available on Maps';

        const techList = Array.isArray(lead.tech_stack) ? lead.tech_stack.join(', ') : (lead.tech_stack || 'Industrial Manufacturing');
        const internalBriefing = 
`[INTERNAL LEAD INTELLIGENCE BRIEFING]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company: ${lead.company_name}
Location: ${lead.area || 'Pune Industrial Corridor'}
Relevance Score: ${lead.score}/100 (${lead.priority || 'High'} Priority)
Target Persona: ${lead.decision_maker || 'Head of Plant Operations / IT Director'}
Contact Phone: ${lead.phone || 'Available on Google Maps'}
Website: ${lead.website || 'N/A'}
Tech Stack & Signals: ${techList}

AI Qualification Signals & Rationale:
${lead.score_reasoning || 'Facility matching Pune MIDC automation profile.'}

Value Proposition:
High-value prospect for BrownBox Innovation's Power BI, SAP ERP pipelines, and shop-floor automation telemetry.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;

        if (alertBriefingBox) {
            alertBriefingBox.value = internalBriefing;
        }

        if (alertModal) alertModal.classList.add('show');
    }

    if (alertModalCloseBtn) {
        alertModalCloseBtn.addEventListener('click', () => {
            if (alertModal) alertModal.classList.remove('show');
        });
    }

    if (alertModal) {
        alertModal.addEventListener('click', (e) => {
            if (e.target === alertModal) {
                alertModal.classList.remove('show');
            }
        });
    }

    // Send Internal Briefing to Telegram
    if (alertSendTgBtn) {
        alertSendTgBtn.addEventListener('click', async () => {
            if (!currentActiveLead) return;
            const orig = alertSendTgBtn.innerHTML;
            alertSendTgBtn.innerHTML = '<span><img src="/ui/icons/clock.png" alt="Sending" class="ui-icon-btn"> Sending...</span>';
            showToast("Sending intelligence alert to your Telegram...");
            try {
                const tgFormatted = `<b>[LEAD INTELLIGENCE BRIEFING]</b>\n\n` +
                    `<b>Company:</b> ${escapeHtml(currentActiveLead.company_name)}\n` +
                    `<b>Area:</b> ${escapeHtml(currentActiveLead.area || 'Pune')}\n` +
                    `<b>Score:</b> ${currentActiveLead.score}/100 (${currentActiveLead.priority} Priority)\n` +
                    `<b>Decision Maker:</b> ${escapeHtml(currentActiveLead.decision_maker || 'Plant Operations / IT Head')}\n` +
                    `<b>Contact Phone:</b> ${escapeHtml(currentActiveLead.phone || 'On Maps')}\n` +
                    `<b>Website:</b> ${escapeHtml(currentActiveLead.website || 'N/A')}\n` +
                    `<b>Tech Stack:</b> ${escapeHtml(Array.isArray(currentActiveLead.tech_stack) ? currentActiveLead.tech_stack.join(', ') : (currentActiveLead.tech_stack || 'Industrial Manufacturing'))}\n\n` +
                    `<b>Signals:</b>\n${escapeHtml(currentActiveLead.score_reasoning || 'Qualified facility.')}`;

                const res = await fetch(`/api/leads/${currentActiveLead.id}/send-alert`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ channel: 'telegram', custom_message: tgFormatted })
                });
                const data = await res.json();
                const tgRes = data.results && data.results.telegram ? data.results.telegram : null;

                if (tgRes && tgRes.success) {
                    alertSendTgBtn.innerHTML = '<span><img src="/ui/icons/check.png" alt="Sent" class="ui-icon-btn"> Sent to Telegram!</span>';
                    showToast("Intelligence alert delivered to your Telegram (@BBI_leads_alert_bot)!");
                    fetchStats();
                    fetchLeads();
                    setTimeout(() => { alertSendTgBtn.innerHTML = orig; }, 2500);
                } else {
                    alertSendTgBtn.innerHTML = orig;
                    const err = tgRes && tgRes.error ? tgRes.error : "Failed to send Telegram message";
                    showToast("Telegram: " + err);
                }
            } catch (err) {
                alertSendTgBtn.innerHTML = orig;
                showToast("Failed to connect to Telegram service");
            }
        });
    }

    // Send Internal Briefing to Email (SMTP)
    if (alertSendEmailBtn) {
        alertSendEmailBtn.addEventListener('click', async () => {
            if (!currentActiveLead) return;
            const orig = alertSendEmailBtn.innerHTML;
            alertSendEmailBtn.innerHTML = '<span><img src="/ui/icons/clock.png" alt="Sending" class="ui-icon-btn"> Sending...</span>';
            showToast("Sending executive briefing directly to your inbox...");
            try {
                const res = await fetch(`/api/leads/${currentActiveLead.id}/send-alert`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ channel: 'email' })
                });
                const data = await res.json();
                const emailRes = data.results && data.results.email ? data.results.email : null;

                if (emailRes && emailRes.success) {
                    alertSendEmailBtn.innerHTML = '<span><img src="/ui/icons/check.png" alt="Sent" class="ui-icon-btn"> Sent to Email!</span>';
                    showToast("Executive briefing emailed to your team!");
                    fetchStats();
                    fetchLeads();
                    setTimeout(() => { alertSendEmailBtn.innerHTML = orig; }, 2500);
                } else {
                    alertSendEmailBtn.innerHTML = orig;
                    const err = emailRes && emailRes.error ? emailRes.error : "Failed to send email";
                    showToast("Email Error: " + err);
                }
            } catch (err) {
                alertSendEmailBtn.innerHTML = orig;
                showToast("Failed to connect to email service");
            }
        });
    }

    // Copy Internal Briefing
    if (alertCopyBtn) {
        alertCopyBtn.addEventListener('click', () => {
            if (alertBriefingBox) {
                navigator.clipboard.writeText(alertBriefingBox.value);
                showToast("Internal briefing copied to clipboard!");
            }
        });
    }

    // ==========================================
    // 3. AUTOMATED ALERT NOTIFICATION SETTINGS MODAL
    // ==========================================
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const settingsCloseBtn = document.getElementById('settings-close-btn');

    const cfgTgEnabled = document.getElementById('cfg-tg-enabled');
    const cfgTgToken = document.getElementById('cfg-tg-token');
    const cfgTgChatid = document.getElementById('cfg-tg-chatid');

    const cfgEmailEnabled = document.getElementById('cfg-email-enabled');
    const cfgEmailTo = document.getElementById('cfg-email-to');
    const cfgSmtpHost = document.getElementById('cfg-smtp-host');
    const cfgSmtpPort = document.getElementById('cfg-smtp-port');
    const cfgSmtpUser = document.getElementById('cfg-smtp-user');
    const cfgSmtpPass = document.getElementById('cfg-smtp-pass');

    const cfgTestBtn = document.getElementById('cfg-test-btn');
    const cfgSaveBtn = document.getElementById('cfg-save-btn');

    window.openAlertSettingsModal = function() {
        loadNotificationSettings();
        const m = document.getElementById('settings-modal');
        if (m) {
            m.classList.add('show');
            m.style.display = 'flex';
        }
    };

    window.closeAlertSettingsModal = function() {
        const m = document.getElementById('settings-modal');
        if (m) {
            m.classList.remove('show');
            m.style.display = 'none';
        }
    };

    if (settingsBtn) {
        settingsBtn.addEventListener('click', window.openAlertSettingsModal);
    }

    if (settingsCloseBtn) {
        settingsCloseBtn.addEventListener('click', window.closeAlertSettingsModal);
    }

    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.remove('show');
            }
        });
    }

    async function loadNotificationSettings() {
        try {
            const res = await fetch('/api/notifications/config');
            const data = await res.json();
            if (data) {
                if (cfgTgEnabled) cfgTgEnabled.checked = data.telegram_enabled !== false;
                if (cfgTgToken) cfgTgToken.value = data.telegram_bot_token || '';
                if (cfgTgChatid) cfgTgChatid.value = data.telegram_chat_id || '';

                if (cfgEmailEnabled) cfgEmailEnabled.checked = !!data.email_enabled;
                if (cfgEmailTo) cfgEmailTo.value = data.email_to || '';
                if (cfgSmtpHost) cfgSmtpHost.value = data.smtp_host || 'smtp.gmail.com';
                if (cfgSmtpPort) cfgSmtpPort.value = data.smtp_port || 587;
                if (cfgSmtpUser) cfgSmtpUser.value = data.smtp_user || '';
                if (cfgSmtpPass) cfgSmtpPass.value = data.smtp_pass_masked || '';
            }
        } catch (e) {
            console.error("Error loading notification config:", e);
        }
    }
    window.loadNotificationSettings = loadNotificationSettings;

    if (cfgSaveBtn) {
        cfgSaveBtn.addEventListener('click', async () => {
            cfgSaveBtn.disabled = true;
            cfgSaveBtn.innerHTML = '<span><img src="/ui/icons/clock.png" class="ui-icon-btn" alt=""> Saving...</span>';

            const payload = {
                whatsapp_enabled: false,
                whatsapp_phone: '',
                whatsapp_apikey: '',
                telegram_enabled: cfgTgEnabled ? cfgTgEnabled.checked : true,
                telegram_bot_token: cfgTgToken ? cfgTgToken.value.trim() : '',
                telegram_chat_id: cfgTgChatid ? cfgTgChatid.value.trim() : '',
                email_enabled: cfgEmailEnabled ? cfgEmailEnabled.checked : false,
                email_to: cfgEmailTo ? cfgEmailTo.value.trim() : '',
                smtp_host: cfgSmtpHost ? cfgSmtpHost.value.trim() : 'smtp.gmail.com',
                smtp_port: cfgSmtpPort ? parseInt(cfgSmtpPort.value) || 587 : 587,
                smtp_user: cfgSmtpUser ? cfgSmtpUser.value.trim() : '',
                smtp_pass: cfgSmtpPass ? cfgSmtpPass.value.trim() : ''
            };

            try {
                const res = await fetch('/api/notifications/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                showToast("Notification channels saved! Telegram bot & Email are active.");
                if (settingsModal) settingsModal.classList.remove('show');
            } catch (e) {
                showToast("Failed to save settings: " + e.message);
            } finally {
                cfgSaveBtn.disabled = false;
                cfgSaveBtn.innerHTML = '<span><img src="/ui/icons/save.png" class="ui-icon-btn" alt=""> Save Settings</span>';
            }
        });
    }

    if (cfgTestBtn) {
        cfgTestBtn.addEventListener('click', async () => {
            cfgTestBtn.disabled = true;
            cfgTestBtn.innerHTML = '<span><img src="/ui/icons/clock.png" class="ui-icon-btn" alt=""> Sending Test Alert...</span>';

            const payload = {
                whatsapp_enabled: false,
                telegram_enabled: cfgTgEnabled ? cfgTgEnabled.checked : true,
                telegram_bot_token: cfgTgToken ? cfgTgToken.value.trim() : '',
                telegram_chat_id: cfgTgChatid ? cfgTgChatid.value.trim() : '',
                email_enabled: cfgEmailEnabled ? cfgEmailEnabled.checked : false,
                email_to: cfgEmailTo ? cfgEmailTo.value.trim() : '',
                smtp_host: cfgSmtpHost ? cfgSmtpHost.value.trim() : 'smtp.gmail.com',
                smtp_port: cfgSmtpPort ? parseInt(cfgSmtpPort.value) || 587 : 587,
                smtp_user: cfgSmtpUser ? cfgSmtpUser.value.trim() : '',
                smtp_pass: cfgSmtpPass ? cfgSmtpPass.value.trim() : ''
            };

            try {
                const res = await fetch('/api/notifications/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                const r = data.results || {};
                let messages = [];

                if (r.telegram) {
                    if (r.telegram.success) {
                        messages.push("Telegram delivered to phone (Success)");
                    } else {
                        messages.push("Telegram: " + (r.telegram.error || "Failed"));
                    }
                }

                if (r.email) {
                    if (r.email.success) {
                        messages.push("Email delivered (Success)");
                    } else {
                        messages.push("Email: " + (r.email.error || "Failed"));
                    }
                }

                if (messages.length === 0) {
                    messages.push("Test alert executed.");
                }

                showToast(messages.join(" • "));
            } catch (e) {
                showToast("Test alert error: " + e.message);
            } finally {
                cfgTestBtn.disabled = false;
                cfgTestBtn.innerHTML = '<span><img src="/ui/icons/flask.png" class="ui-icon-btn" alt=""> Send Test Alert Now</span>';
            }
        });
    }

    // ==========================================
    // 4. DISPATCHED ALERTS LOG MODAL
    // ==========================================
    async function openDispatchedAlertsModal() {
        if (!dispatchedModal) return;
        dispatchedModal.classList.add('show');
        dispatchedModal.style.display = 'flex';

        if (dispatchedListContainer) {
            dispatchedListContainer.innerHTML = `
                <div style="text-align:center; padding: 3rem; color: #94a3b8;">
                    <div class="spinner" style="display:inline-block; margin-bottom:1rem; border-top-color:#38bdf8; width:30px; height:30px;"></div>
                    <div style="font-size:0.9rem;">Loading dispatched lead intelligence alerts...</div>
                </div>
            `;
        }

        try {
            const res = await fetch('/api/leads?alerted_only=true');
            allDispatchedLeads = await res.json();
            renderDispatchedAlerts(allDispatchedLeads);
        } catch (err) {
            console.error("Error loading dispatched alerts:", err);
            if (dispatchedListContainer) {
                dispatchedListContainer.innerHTML = `
                    <div style="text-align:center; padding: 2.5rem; color: #ef4444;">
                        Failed to load dispatched alerts. Please check your connection.
                    </div>
                `;
            }
        }
    }
    window.openDispatchedAlertsModal = openDispatchedAlertsModal;

    function closeDispatchedAlertsModal() {
        if (dispatchedModal) {
            dispatchedModal.classList.remove('show');
            dispatchedModal.style.display = 'none';
        }
    }
    window.closeDispatchedAlertsModal = closeDispatchedAlertsModal;

    function renderDispatchedAlerts(leads) {
            if (!leads || leads.length === 0) {
            dispatchedListContainer.innerHTML = `
                <div style="text-align: center; padding: 3.5rem 1.5rem; color: #94a3b8;">
                    <img src="/ui/icons/rocket.png" style="width: 48px; height: 48px; margin-bottom: 0.8rem; filter: drop-shadow(0 4px 12px rgba(6,182,212,0.3));" alt="Rocket">
                    <h4 style="color: #f8fafc; font-size: 1.15rem; margin-bottom: 0.5rem; font-weight:700;">No Alerts Dispatched Yet</h4>
                    <p style="font-size: 0.86rem; max-width: 440px; margin: 0 auto 1.25rem auto; line-height: 1.6; color: #cbd5e1;">
                        No lead alerts have been dispatched so far. Click <strong>"Alert Me"</strong> on any High Priority card or let Auto-Pilot automatically deliver alerts to your Telegram (@BBI_leads_alert_bot) and Email.
                    </p>
                </div>
            `;
            return;
        }

        const cardsHtml = leads.map(lead => {
            let techPillsHtml = '';
            if (lead.tech_stack && lead.tech_stack.length > 0) {
                techPillsHtml = lead.tech_stack.map(tech => {
                    const isKey = ['SAP', 'Power BI', 'SQL Server', 'SCADA', 'MES'].some(k => tech.toLowerCase().includes(k.toLowerCase()));
                    return `<span class="tech-pill ${isKey ? 'highlight' : ''}">${escapeHtml(tech)}</span>`;
                }).join('');
            } else {
                techPillsHtml = '<span class="tech-pill">Industrial Manufacturing</span>';
            }

            const displayArea = lead.area || 'Pune MIDC';
            const phoneSnippet = lead.phone ? `<a href="tel:${escapeHtml(lead.phone)}" style="color:#93c5fd; text-decoration:none; font-family:var(--font-mono); font-weight:600;">${escapeHtml(lead.phone)}</a>` : '<span style="color:#64748b;">Phone on Maps</span>';
            const websiteSnippet = lead.website ? `<a href="${lead.website}" target="_blank" style="color:#38bdf8; text-decoration:none; font-weight:600;"><img src="/ui/icons/globe.png" class="ui-icon-inline" alt=""> ${escapeHtml(lead.website)}</a>` : '<span style="color:#64748b;">No Website</span>';
            const dispatchTime = lead.created_at ? lead.created_at : 'Recently';

            return `
                <div class="dispatched-card" id="disp-card-${lead.id}">
                    <div class="disp-header-row">
                        <div class="disp-title-group">
                            <div class="disp-company-title">
                                <span><img src="/ui/icons/building.png" class="ui-icon-inline" alt=""> ${escapeHtml(lead.company_name)}</span>
                                <span class="card-area-pill" style="font-size: 0.78rem; padding: 2px 8px;">
                                    <img src="/ui/icons/location.png" class="ui-icon-inline" alt="">
                                    <span>${escapeHtml(displayArea)}</span>
                                </span>
                            </div>
                            <div class="disp-channel-pills">
                                <span class="disp-channel-pill disp-channel-tg" title="Delivered to your Telegram @BBI_leads_alert_bot">
                                    <img src="/ui/icons/telegram.png" class="ui-icon-inline" alt=""> Telegram (@BBI_leads_alert_bot)
                                </span>
                                <span class="disp-channel-pill disp-channel-email" title="Delivered via direct SMTP email">
                                    <img src="/ui/icons/mail.png" class="ui-icon-inline" alt=""> Direct Email
                                </span>
                                <span style="font-size: 0.78rem; color: #94a3b8; margin-left: 0.4rem; display: inline-flex; align-items: center; gap: 4px;">
                                    <img src="/ui/icons/clock.png" class="ui-icon-inline" alt=""> Logged: ${escapeHtml(dispatchTime)}
                                </span>
                            </div>
                        </div>
                        <div class="card-score-pill" style="align-self: flex-start;">
                            <img src="/ui/icons/star.png" class="ui-icon-inline" alt="">
                            <span>${lead.score}/100</span>
                            <span style="font-size: 0.78rem; opacity: 0.9;">${lead.priority || 'High'}</span>
                        </div>
                    </div>

                    <div class="disp-meta-grid">
                        <div class="disp-meta-item">
                            <span class="label"><img src="/ui/icons/target.png" class="ui-icon-inline" alt=""> Target Persona:</span>
                            <span class="val" style="color:#a5b4fc; font-weight:600;">${escapeHtml(lead.decision_maker || 'Head of IT / Plant Operations')}</span>
                        </div>
                        <div class="disp-meta-item">
                            <span class="label"><img src="/ui/icons/phone.png" class="ui-icon-inline" alt=""> Phone:</span>
                            <span class="val">${phoneSnippet}</span>
                        </div>
                        <div class="disp-meta-item">
                            <span class="label"><img src="/ui/icons/globe.png" class="ui-icon-inline" alt=""> Website:</span>
                            <span class="val">${websiteSnippet}</span>
                        </div>
                        <div class="disp-meta-item">
                            <span class="label"><img src="/ui/icons/location.png" class="ui-icon-inline" alt=""> Address:</span>
                            <span class="val" style="font-size:0.85rem;">${escapeHtml(lead.address || displayArea)}</span>
                        </div>
                    </div>

                    <div class="tech-tag-container" style="margin-top: 0;">
                        ${techPillsHtml}
                    </div>

                    <div class="disp-briefing-box">
                        <div class="title" style="display: flex; align-items: center; gap: 6px;">
                            <img src="/ui/icons/search.png" class="ui-icon-inline" alt=""> Intelligence Briefing Sent in Alert:
                        </div>
                        <div>
                            ${escapeHtml(lead.score_reasoning || 'Qualified facility matching Pune MIDC automation profile.')}
                        </div>
                    </div>

                    <div class="disp-actions-row">
                        <div style="font-size: 0.82rem; color: #10b981; font-weight: 600; display: flex; align-items: center; gap: 0.4rem;">
                            <img src="/ui/icons/check.png" class="ui-icon-inline" alt=""> Alert Delivered to Channels
                        </div>
                        <div class="disp-btn-group">
                            <button class="btn btn-secondary btn-sm disp-copy-btn" data-id="${lead.id}" title="Copy internal intelligence briefing">
                                <span><img src="/ui/icons/copy.png" class="ui-icon-btn" alt=""> Copy Briefing</span>
                            </button>
                            <button class="btn btn-secondary btn-sm disp-pitch-btn" data-id="${lead.id}" title="Open client-facing pitch proposal">
                                <span><img src="/ui/icons/chat.png" class="ui-icon-btn" alt=""> View Pitch</span>
                            </button>
                            <button class="btn btn-secondary btn-sm disp-resend-btn" data-id="${lead.id}" title="Re-dispatch alert to Telegram & Email" style="border-color: rgba(6,182,212,0.4); color: #67e8f9;">
                                <span><img src="/ui/icons/repeat.png" class="ui-icon-btn" alt=""> Re-Send Alert</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        dispatchedListContainer.innerHTML = cardsHtml;
        attachDispatchedCardListeners(leads);
    }

    function attachDispatchedCardListeners(leads) {
        // Copy Briefing
        document.querySelectorAll('.disp-copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const leadId = parseInt(btn.getAttribute('data-id'));
                const lead = leads.find(l => l.id === leadId);
                if (!lead) return;
                const techList = Array.isArray(lead.tech_stack) ? lead.tech_stack.join(', ') : (lead.tech_stack || 'Industrial Manufacturing');
                const text = 
`[DISPATCHED LEAD INTELLIGENCE ALERT]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company: ${lead.company_name}
Location: ${lead.area || 'Pune Industrial Corridor'}
Relevance Score: ${lead.score}/100 (${lead.priority || 'High'} Priority)
Target Persona: ${lead.decision_maker || 'Head of Plant Operations / IT Director'}
Contact Phone: ${lead.phone || 'Available on Google Maps'}
Website: ${lead.website || 'N/A'}
Tech Stack & Signals: ${techList}

AI Qualification Signals & Rationale:
${lead.score_reasoning || 'Facility matching Pune MIDC automation profile.'}

Value Proposition:
High-value prospect for BrownBox Innovation's Power BI, SAP ERP pipelines, and shop-floor automation telemetry.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
                navigator.clipboard.writeText(text);
                showToast(`Briefing for ${lead.company_name} copied to clipboard!`);
            });
        });

        // View Pitch
        document.querySelectorAll('.disp-pitch-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const leadId = parseInt(btn.getAttribute('data-id'));
                const lead = leads.find(l => l.id === leadId);
                if (lead) {
                    openPitchModal(lead);
                }
            });
        });

        // Re-Send Alert
        document.querySelectorAll('.disp-resend-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const leadId = parseInt(btn.getAttribute('data-id'));
                const lead = leads.find(l => l.id === leadId);
                if (!lead) return;

                const origHtml = btn.innerHTML;
                btn.disabled = true;
                btn.innerHTML = '<span><img src="/ui/icons/clock.png" class="ui-icon-btn" alt=""> Sending...</span>';
                showToast(`Re-dispatching alert for ${lead.company_name} to Telegram & Email...`);

                try {
                    const res = await fetch(`/api/leads/${lead.id}/send-alert`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ channel: 'all' })
                    });
                    const data = await res.json();
                    btn.innerHTML = '<span><img src="/ui/icons/check.png" class="ui-icon-btn" alt=""> Dispatched!</span>';
                    showToast(`Alert re-dispatched to Telegram & Email for ${lead.company_name}!`);
                    fetchStats();
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.innerHTML = origHtml;
                    }, 2500);
                } catch (e) {
                    btn.disabled = false;
                    btn.innerHTML = origHtml;
                    showToast("Failed to re-send alert: " + e.message);
                }
            });
        });
    }

    // Search filter inside dispatched modal
    if (dispatchedSearchInput) {
        dispatchedSearchInput.addEventListener('input', () => {
            const query = dispatchedSearchInput.value.trim().toLowerCase();
            if (!query) {
                renderDispatchedAlerts(allDispatchedLeads);
                return;
            }
            const filtered = allDispatchedLeads.filter(l => {
                const name = (l.company_name || '').toLowerCase();
                const area = (l.area || '').toLowerCase();
                const persona = (l.decision_maker || '').toLowerCase();
                const phone = (l.phone || '').toLowerCase();
                const tech = Array.isArray(l.tech_stack) ? l.tech_stack.join(' ').toLowerCase() : (l.tech_stack || '').toLowerCase();
                const reason = (l.score_reasoning || '').toLowerCase();
                return name.includes(query) || area.includes(query) || persona.includes(query) || phone.includes(query) || tech.includes(query) || reason.includes(query);
            });
            renderDispatchedAlerts(filtered);
        });
    }

    // View in Main Grid button
    if (dispatchedViewGridBtn) {
        dispatchedViewGridBtn.addEventListener('click', () => {
            closeDispatchedAlertsModal();
            // Switch priority filter to Alerted
            document.querySelectorAll('.filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            const alertedTab = document.querySelector('.filter-tabs .tab-btn[data-filter="Alerted"]');
            if (alertedTab) alertedTab.classList.add('active');
            currentPriority = 'Alerted';
            fetchLeads();
            showToast("Filtering main dashboard to Dispatched Leads");
        });
    }

    // Card Alerted click handler
    if (cardAlerted) {
        cardAlerted.addEventListener('click', openDispatchedAlertsModal);
    }

    // Close button handler
    if (dispatchedModalCloseBtn) {
        dispatchedModalCloseBtn.addEventListener('click', closeDispatchedAlertsModal);
    }

    // Backdrop click handler
    if (dispatchedModal) {
        dispatchedModal.addEventListener('click', (e) => {
            if (e.target === dispatchedModal) {
                closeDispatchedAlertsModal();
            }
        });
    }

    // ==========================================
    // ENTERPRISE SUITE: JOB INTENT, ENRICHMENT, DRIP
    // ==========================================
    const jobsScrapeBtn = document.getElementById('jobs-scrape-btn');
    if (jobsScrapeBtn) {
        jobsScrapeBtn.addEventListener('click', async () => {
            jobsScrapeBtn.innerHTML = '<span>Scanning Portals...</span>';
            jobsScrapeBtn.disabled = true;
            showToast("Searching Naukri & Job Portals for Pune SAP, Power BI & Automation openings...");

            try {
                const res = await fetch('/api/jobs/scrape?limit=8', { method: 'POST' });
                const data = await res.json();
                showToast(`Found ${data.jobs_found || 0} active hiring intent postings! Added ${data.leads_added || 0} new leads.`);
                fetchStats();
                fetchLeads();
            } catch (e) {
                showToast("Job intent scan failed");
            } finally {
                jobsScrapeBtn.innerHTML = '<span>Scan Job Intent</span>';
                jobsScrapeBtn.disabled = false;
            }
        });
    }

    const enrichAllBtn = document.getElementById('enrich-all-btn');
    if (enrichAllBtn) {
        enrichAllBtn.addEventListener('click', async () => {
            enrichAllBtn.innerHTML = '<span>Enriching Database...</span>';
            enrichAllBtn.disabled = true;
            showToast("Enriching leads with Decision Makers, LinkedIn profiles, MCA financials, and Technographics...");

            try {
                const res = await fetch('/api/leads/enrich-all', { method: 'POST' });
                const data = await res.json();
                showToast(`Enriched ${data.enriched_count || 0} leads with enterprise contacts and financials!`);
                fetchLeads();
            } catch (e) {
                showToast("Enrichment batch failed");
            } finally {
                enrichAllBtn.innerHTML = '<span>Enrich All Intel</span>';
                enrichAllBtn.disabled = false;
            }
        });
    }

    const runDripBtn = document.getElementById('run-drip-btn');
    if (runDripBtn) {
        runDripBtn.addEventListener('click', async () => {
            runDripBtn.innerHTML = '<span>Processing Sequences...</span>';
            runDripBtn.disabled = true;
            showToast("Executing due Day 1 / Day 3 / Day 7 follow-up sequences...");

            try {
                const res = await fetch('/api/campaigns/run-due', { method: 'POST' });
                const data = await res.json();
                showToast(`Processed ${data.advanced_leads || 0} due drip campaign touches!`);
                fetchLeads();
            } catch (e) {
                showToast("Drip campaign processing failed");
            } finally {
                runDripBtn.innerHTML = '<span>Run Drip Follow-ups</span>';
                runDripBtn.disabled = false;
            }
        });
    }

    // Drip Modal Elements & Functions
    const dripModal = document.getElementById('drip-modal');
    const dripModalCloseBtn = document.getElementById('drip-modal-close-btn');
    const dripModalCompanyName = document.getElementById('drip-modal-company-name');
    const dripStatusBadge = document.getElementById('drip-status-badge');
    const dripStepBadge = document.getElementById('drip-step-badge');
    const dripNextDate = document.getElementById('drip-next-date');
    const dripRecipientEmail = document.getElementById('drip-recipient-email');
    const dripSubjectBox = document.getElementById('drip-subject-box');
    const dripBodyBox = document.getElementById('drip-body-box');
    const dripCopyBtn = document.getElementById('drip-copy-btn');
    const dripAdvanceNowBtn = document.getElementById('drip-advance-now-btn');

    let currentDripData = null;
    let selectedDripStep = 1;

    async function openDripModal(leadId) {
        if (!dripModal) return;
        dripModal.classList.add('show');
        dripModalCompanyName.textContent = "Loading Sequence...";

        try {
            const res = await fetch(`/api/campaigns/${leadId}/templates`);
            const data = await res.json();
            currentDripData = data;
            dripModalCompanyName.textContent = data.company_name;
            if (dripRecipientEmail) dripRecipientEmail.value = data.target_email || "";
            dripStatusBadge.textContent = data.campaign_status || "Active";
            dripStepBadge.textContent = `Step ${data.current_step || 0} / 3`;
            dripNextDate.textContent = data.next_campaign_date ? `Next: ${data.next_campaign_date}` : (data.current_step >= 3 ? "Sequence Finished" : "Ready for Step 1");

            selectedDripStep = Math.max(1, Math.min(3, (data.current_step || 0) + 1));
            renderDripStepPreview();
        } catch (e) {
            showToast("Failed to load drip templates");
        }
    }

    function renderDripStepPreview() {
        if (!currentDripData || !currentDripData.steps) return;
        document.querySelectorAll('.drip-step-tab').forEach(t => {
            const stepNum = parseInt(t.getAttribute('data-step'));
            t.classList.toggle('active', stepNum === selectedDripStep);
        });

        const stepInfo = currentDripData.steps[selectedDripStep] || {};
        dripSubjectBox.value = stepInfo.subject || "";
        dripBodyBox.value = stepInfo.body || "";
        dripAdvanceNowBtn.innerHTML = `<span><img src="/ui/icons/rocket.png" class="ui-icon-btn" alt=""> Dispatch Step ${selectedDripStep} Now</span>`;
    }

    // Step Tab Clicking
    document.querySelectorAll('.drip-step-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            selectedDripStep = parseInt(tab.getAttribute('data-step'));
            renderDripStepPreview();
        });
    });

    if (dripModalCloseBtn) {
        dripModalCloseBtn.addEventListener('click', () => {
            dripModal.classList.remove('show');
        });
    }

    if (dripModal) {
        dripModal.addEventListener('click', (e) => {
            if (e.target === dripModal) dripModal.classList.remove('show');
        });
    }

    if (dripCopyBtn) {
        dripCopyBtn.addEventListener('click', () => {
            const text = `Subject: ${dripSubjectBox.value}\n\n${dripBodyBox.value}`;
            navigator.clipboard.writeText(text);
            showToast("Outreach message copied to clipboard!");
        });
    }

    if (dripAdvanceNowBtn) {
        dripAdvanceNowBtn.addEventListener('click', async () => {
            if (!currentDripData) return;
            const orig = dripAdvanceNowBtn.innerHTML;
            dripAdvanceNowBtn.innerHTML = '<span><img src="/ui/icons/clock.png" class="ui-icon-btn" alt=""> Dispatching...</span>';
            dripAdvanceNowBtn.disabled = true;

            const targetEmailVal = dripRecipientEmail ? dripRecipientEmail.value.trim() : '';

            try {
                const res = await fetch(`/api/campaigns/${currentDripData.lead_id}/advance`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        force_step: selectedDripStep,
                        custom_email: targetEmailVal
                    })
                });
                const resData = await res.json();
                if (resData.success) {
                    showToast(`Step ${selectedDripStep} Dispatched via ${resData.dispatched_channels && resData.dispatched_channels.length ? resData.dispatched_channels.join(', ') : 'CRM Record'}!`);
                    dripModal.classList.remove('show');
                    fetchLeads();
                } else {
                    showToast(resData.error || "Dispatch failed");
                }
            } catch (e) {
                showToast("Error dispatching drip step");
            } finally {
                dripAdvanceNowBtn.innerHTML = orig;
                dripAdvanceNowBtn.disabled = false;
            }
        });
    }

    // Global ESC key listener to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeLeadDetailModal();
            if (pitchModal) pitchModal.classList.remove('show');
            if (alertModal) alertModal.classList.remove('show');
            if (dripModal) dripModal.classList.remove('show');
            if (dispatchedModal) {
                dispatchedModal.classList.remove('show');
                dispatchedModal.style.display = 'none';
            }
            if (settingsModal) {
                settingsModal.classList.remove('show');
                settingsModal.style.display = 'none';
            }
        }
    });

    // Helper: Toast
    function showToast(message) {
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3500);
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
