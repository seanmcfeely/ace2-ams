import { mount } from "@cypress/vue";

import PrimeVue from "primevue/config";

import UtcDatePicker from "@/components/UserInterface/UtcDatePicker.vue";
import { createPinia } from "pinia";
import type CSS from "csstype";

interface UtcDatePickerProps {
  modelValue: Date | undefined;
  placeholder?: string;
  overlayStyle?: CSS.Properties;
}

const defaultProps: UtcDatePickerProps = {
  modelValue: undefined,
};

function factory(props: UtcDatePickerProps = defaultProps) {
  mount(UtcDatePicker, {
    global: {
      plugins: [PrimeVue, createPinia()],
    },
    propsData: props,
  });
}

describe("UtcDatePicker", () => {
  it("renders correctly when not given date prop or placeholder prop", () => {
    factory();
    cy.findByPlaceholderText("Select a date")
      .should("be.visible")
      .and("be.empty");
  });
  it("renders correctly when not given a date prop, but given a placeholder prop", () => {
    factory({ modelValue: undefined, placeholder: "Custom placeholder" });
    cy.findByPlaceholderText("Custom placeholder")
      .should("be.visible")
      .and("be.empty");
  });
  it("renders correctly when given a date prop", () => {
    const date = new Date(2022, 2, 2, 12, 0, 0, 0);
    factory({ modelValue: date });
    cy.findByDisplayValue("03/02/2022 17:00:00").should("be.visible");
    cy.findByDisplayValue("03/02/2022 17:00:00").click();
    cy.get(".p-hour-picker").find("span").eq(1).should("contain.text", "17");
    cy.get(".p-minute-picker").find("span").eq(1).should("contain.text", "00");
    cy.get(".p-second-picker").find("span").eq(1).should("contain.text", "00");
  });
  it("correctly updates date prop when a new date is typed", () => {
    const date = new Date(2022, 2, 2, 12, 0, 0, 0);
    factory({
      modelValue: date,
      overlayStyle: { width: "450px", marginTop: "4rem" },
    });
    cy.findByDisplayValue("03/02/2022 17:00:00")
      .click()
      .clear()
      .type("03/02/2022 18:00:00")
      .type("{enter}");
    cy.findByDisplayValue("03/02/2022 18:00:00").should("be.visible");
    cy.get("body").then(() => {
      expect(Cypress.vueWrapper.emitted("update:modelValue")).to.have.length;
      expect(
        Cypress.vueWrapper.emitted("update:modelValue")[0][0],
      ).to.deep.equal(new Date(2022, 2, 2, 13, 0, 0, 0));
    });
  });
  it("correctly updates date prop when a new date is selected through calendar", () => {
    const date = new Date(2022, 2, 2, 12, 0, 0, 0);
    factory({
      modelValue: date,
      overlayStyle: { width: "450px", marginTop: "4rem" },
    });
    cy.findByDisplayValue("03/02/2022 17:00:00").click();
    cy.get(".p-hour-picker").find("span").eq(0).click();
    cy.get(".p-minute-picker").find("span").eq(0).click();
    cy.get(".p-second-picker").find("span").eq(0).click();
    cy.findByDisplayValue("03/02/2022 18:01:01").should("be.visible");
    cy.get('[name="save-date"]').click();
    cy.get("body").then(() => {
      expect(Cypress.vueWrapper.emitted("update:modelValue")).to.have.length;
      expect(
        Cypress.vueWrapper.emitted("update:modelValue")[0][0],
      ).to.deep.equal(new Date(2022, 2, 2, 13, 1, 1, 0));
    });
  });
  it("correctly updates when prop is changed", () => {
    const date = new Date(2022, 2, 2, 12, 0, 0, 0);
    factory({
      modelValue: date,
      overlayStyle: { width: "450px", marginTop: "4rem" },
    });
    cy.get("body").then(() => {
      cy.findByDisplayValue("03/02/2022 17:00:00").should("be.visible");
    });
    cy.get("body").then(() => {
      Cypress.vueWrapper.setProps({
        modelValue: new Date(2022, 2, 2, 13, 1, 1),
      });
      cy.findByDisplayValue("03/02/2022 18:01:01").should("be.visible").click();
      cy.get(".p-hour-picker").find("span").eq(1).should("contain.text", "18");
      cy.get(".p-minute-picker")
        .find("span")
        .eq(1)
        .should("contain.text", "01");
      cy.get(".p-second-picker")
        .find("span")
        .eq(1)
        .should("contain.text", "01");
    });
  });
  it("correctly updates date prop when date is cleared", () => {
    const date = new Date(2022, 2, 2, 12, 0, 0, 0);
    factory({
      modelValue: date,
      overlayStyle: { width: "450px", marginTop: "4rem" },
    });
    cy.get("body").then(() => {
      cy.findByDisplayValue("03/02/2022 17:00:00").should("be.visible");
    });
    cy.get("body").then(() => {
      Cypress.vueWrapper.setProps({
        modelValue: undefined,
      });
      cy.findByPlaceholderText("Select a date")
        .should("be.visible")
        .and("be.empty");
    });
  });
  it("doesn't update date prop and displays input as invalid if typed date is invalid", () => {
    const date = new Date(2022, 2, 2, 12, 0, 0, 0);
    factory({
      modelValue: date,
      overlayStyle: { width: "450px", marginTop: "4rem" },
    });
    cy.findByDisplayValue("03/02/2022 17:00:00")
      .click()
      .clear()
      .type("invalid")
      .type("{enter}");
    cy.findByDisplayValue("invalid").should("be.visible");
    cy.get("input").should("have.class", "p-invalid");
    cy.get("body").then(() => {
      expect(Cypress.vueWrapper.emitted("update:modelValue")).to.not.exist;
    });
  });
});
