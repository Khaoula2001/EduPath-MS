import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RiskStudentsTable } from './risk-students-table';

describe('RiskStudentsTable', () => {
  let component: RiskStudentsTable;
  let fixture: ComponentFixture<RiskStudentsTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskStudentsTable]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RiskStudentsTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
