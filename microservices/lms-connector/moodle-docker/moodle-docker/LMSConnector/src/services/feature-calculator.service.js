class FeatureCalculatorService {
  calculateEngagementMetrics(logs = []) {
    const activityCount = logs.length;
    const totalClicks = logs.filter(l => l.action === 'view' || l.action === 'clicked').length;
    const firstActivityDay = logs.length ? new Date(logs[0].timecreated * 1000) : null;
    const lastActivityDay = logs.length ? new Date(logs[logs.length - 1].timecreated * 1000) : null;

    const days = new Map();
    logs.forEach(l => {
      const d = new Date(l.timecreated * 1000).toISOString().slice(0,10);
      days.set(d, (days.get(d) || 0) + 1);
    });
    const activeDays = days.size;

    const clicksPerActivity = activityCount ? totalClicks / activityCount : 0;
    const avgClicksPerActivity = clicksPerActivity;
    const mean = avgClicksPerActivity;
    const clickStd = 0; // simple placeholder, real calc requires per-activity clicks

    const studyDuration = firstActivityDay && lastActivityDay
      ? Math.ceil((lastActivityDay - firstActivityDay) / (1000*60*60*24))
      : 0;

    const engagementIntensity = activityCount ? totalClicks / Math.max(studyDuration, 1) : 0;

    const regularityIndex = activeDays && studyDuration
      ? activeDays / Math.max(studyDuration, 1)
      : 0;

    const daysWithoutActivity = Math.max(studyDuration - activeDays, 0);

    return {
      total_clicks: totalClicks,
      activity_count: activityCount,
      avg_clicks_per_activity: Number(avgClicksPerActivity.toFixed(2)),
      click_std: Number(clickStd.toFixed(2)),
      first_activity_day: firstActivityDay,
      last_activity_day: lastActivityDay,
      active_days: activeDays,
      days_without_activity: daysWithoutActivity,
      regularity_index: Number(regularityIndex.toFixed(2)),
      engagement_intensity: Number(engagementIntensity.toFixed(2)),
      study_duration: studyDuration,
    };
  }

  calculateGradeMetrics(grades = []) {
    if (!grades.length) return { mean_score: null, score_std: null, latest_assessment_score: null };
    const vals = grades.map(g => Number(g.finalgrade || g.rawgrade || 0)).filter(v => !isNaN(v));
    if (!vals.length) return { mean_score: null, score_std: null, latest_assessment_score: null };
    const mean = vals.reduce((a,b)=>a+b,0) / vals.length;
    const variance = vals.reduce((a,b)=>a + Math.pow(b-mean,2), 0) / vals.length;
    const std = Math.sqrt(variance);
    const latest = grades.sort((a,b) => (a.timemodified||0) - (b.timemodified||0)).slice(-1)[0];
    const latestScore = latest ? (latest.finalgrade || latest.rawgrade || null) : null;
    return { mean_score: Number(mean.toFixed(2)), score_std: Number(std.toFixed(2)), latest_assessment_score: latestScore };
  }

  calculateDropoutRisk(engagementMetrics, gradeMetrics) {
    const lowEngagement = (engagementMetrics.activity_count || 0) < 10 || (engagementMetrics.regularity_index || 0) < 0.3;
    const lowGrades = (gradeMetrics.mean_score || 0) < 50;
    const risk = (lowEngagement ? 1 : 0) + (lowGrades ? 1 : 0);
    // Map to 0-2 risk signal for simplicity
    return Math.min(risk, 2);
  }

  calculateEngagementDropRate(logs = []) {
    if (logs.length < 2) return 0;
    const midIndex = Math.floor(logs.length / 2);
    const early = logs.slice(0, midIndex).length;
    const late = logs.slice(midIndex).length;
    const dropRate = early ? (early - late) / early : 0;
    return Number(dropRate.toFixed(2));
  }

  calculateAgeBand(profile) {
    // If age known (custom), otherwise map by band string
    const band = profile?.age_band || profile?.age || null;
    if (!band) return null;
    const s = String(band).toLowerCase();
    if (s.includes('0-17')) return '0-17';
    if (s.includes('18-25') || s.includes('18')) return '18-25';
    if (s.includes('26-35') || s.includes('26')) return '26-35';
    if (s.includes('36-45') || s.includes('36')) return '36-45';
    if (s.includes('46-55') || s.includes('46')) return '46-55';
    return '55+';
  }

  calculateProgressRate(submissions = [], courseModules = []) {
    const submitted = submissions.filter(s => s.status === 'submitted' || s.status === 'submitted_for_grading').length;
    const total = courseModules.length || 1;
    const rate = submitted / total;
    return Number(rate.toFixed(2));
  }
}

module.exports = FeatureCalculatorService;
