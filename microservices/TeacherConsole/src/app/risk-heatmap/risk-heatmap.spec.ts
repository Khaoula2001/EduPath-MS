import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RiskHeatmap } from './risk-heatmap';

describe('RiskHeatmap', () => {
  let component: RiskHeatmap;
  let fixture: ComponentFixture<RiskHeatmap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskHeatmap]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RiskHeatmap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
